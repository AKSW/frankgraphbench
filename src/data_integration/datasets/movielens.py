import os
import re
import queue
from io import BytesIO
from collections import defaultdict


from string import Template
from ..dataset import Dataset

import pandas as pd
from tqdm import tqdm
from thefuzz import process
from SPARQLWrapper import CSV


class MovieLens(Dataset):
    """
    General MovieLens(Dataset) class for data integration between DBpedia and MovieLens
    """

    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers)
        self.map_fields = {"item_id": "item_id::string", "URI": "URI::string"}
        self.map_query_template = Template(
            """
            PREFIX dct:  <http://purl.org/dc/terms/>
            PREFIX dbo:  <http://dbpedia.org/ontology/>
            PREFIX dbr:  <http://dbpedia.org/resource/>
            PREFIX rdf:	 <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?film WHERE {
                {
                    ?film rdf:type dbo:Film .
                    ?film dct:subject $year_category .
                    ?film rdfs:label ?label .
                    FILTER regex(?label, "$name_regex", "i")
                }
                UNION
                {
                    ?film rdf:type dbo:Film .
                    ?film dct:subject $year_category .
                    ?tmp dbo:wikiPageRedirects ?film .
                    ?tmp rdfs:label ?label .
                    FILTER regex(?label, "$name_regex", "i") .
                }
            }
        """
        )
        self.enrich_fields = {
            "item_id": "item_id::string",
            "abstract": "abstract::string",
            "producer": "producer::string_list",
            "distributor": "distributor::string_list",
            "writer": "writer::string_list",
            "cinematography": "cinematography::string_list",
            "subject": "subject::string_list",
            "starring": "starring::string_list",
            "director": "director::string_list"
        }
        self.enrich_query_template = Template(
            """
            PREFIX dct:  <http://purl.org/dc/terms/>
            PREFIX dbo:  <http://dbpedia.org/ontology/>
            PREFIX dbr:  <http://dbpedia.org/resource/>
            PREFIX rdf:	 <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT
                ?abstract 
                (GROUP_CONCAT(DISTINCT ?producer; SEPARATOR="::") AS ?producer)
                (GROUP_CONCAT(DISTINCT ?distributor; SEPARATOR="::") AS ?distributor)
                (GROUP_CONCAT(DISTINCT ?writer; SEPARATOR="::") AS ?writer)
                (GROUP_CONCAT(DISTINCT ?cinematography; SEPARATOR="::") AS ?cinematography)
                (GROUP_CONCAT(DISTINCT ?subject; SEPARATOR="::") AS ?subject)
                (GROUP_CONCAT(DISTINCT ?starring; SEPARATOR="::") AS ?starring)
                (GROUP_CONCAT(DISTINCT ?director; SEPARATOR="::") AS ?director)
            WHERE {
                OPTIONAL { <$URI>   dct:subject         ?subject            }   .
                OPTIONAL { <$URI>   dbo:starring        ?starring           }   .
                OPTIONAL { <$URI>   dbo:director        ?director           }   .
                OPTIONAL { <$URI>   dbo:abstract        ?abstract           }   .
                OPTIONAL { <$URI>   dbo:producer        ?producer           }   .
                OPTIONAL { <$URI>   dbo:distributor     ?distributor        }   .
                OPTIONAL { <$URI>   dbo:writer          ?writer             }   .
                OPTIONAL { <$URI>   dbo:cinematography  ?cinematography     }   .

                FILTER(LANG(?abstract) = 'en')
            }
        """
        )

    def _extract_title(self, title):
        regex = re.compile(r"\((\d{4})\)")
        rgx_match = regex.search(title)
        year_start, _ = rgx_match.span()
        movie_title = title[: year_start - 1].strip()

        # removing parenthesis (name of the film in other languages)
        movie_title = [s.split(")")[-1] for s in movie_title.split("(")][0]

        # Reversing titles with X, The
        movie_title = movie_title.split(",")
        movie_title = [movie_title[-1].strip()] + [
            title.strip() for title in movie_title[:-1]
        ]
        movie_title = " ".join(movie_title)

        movie_title = movie_title.strip()
        return movie_title

    def _extract_year(self, title):
        regex = re.compile(r"\((\d{4})\)")
        rgx_match = regex.search(title)
        movie_year = rgx_match.group()
        movie_year = int(movie_year[1:-1])
        return movie_year

    def entity_linking(self, df_item) -> pd.DataFrame():
        q = queue.Queue()
        for idx, row in df_item[["movie_title", "movie_year", "item_id"]].iterrows():
            query = self.get_map_query(row["movie_title"], row["movie_year"])
            q.put((row["item_id"], query))

        if self.n_workers > 1:
            responses = self.parallel_queries(q)
        else:
            responses = self.sequential_queries(q)

        URI_mapping = defaultdict(dict)
        for response in tqdm(responses, desc="Disambiguating query return"):
            candidate_URIs = []
            idx, result = response
            for binding in result["results"]["bindings"]:
                URI = binding["film"]["value"]
                candidate_URIs.append(URI)

            expected_URI = f"http://dbpedia.org/resource/{df_item.loc[df_item.item_id == idx]['movie_title']}"
            str_matching_result = process.extractOne(expected_URI, candidate_URIs)

            if str_matching_result is not None:
                URI, _ = str_matching_result
                URI_mapping[idx] = URI

        df_map = pd.DataFrame({"item_id": df_item["item_id"]})
        df_map.set_index("item_id")
        df_map["URI"] = df_map["item_id"].apply(lambda id: URI_mapping.get(id))
        df_map = df_map.rename(self.map_fields, axis=1)

        return df_map

    def get_map_query(self, title, year) -> str:
        # title = title.translate(self._special_chars_map)
        title = title.replace(" ", ".*")
        title = "^" + title

        params = {
            "name_regex": title,
            "year_category": f"dbr:Category:{str(year)}_films",
        }
        query = self.map_query_template.substitute(**params)
        return query

    def enrich(self, df_map) -> pd.DataFrame():
        df_map = df_map[df_map[self.map_fields["URI"]].notna()]

        q = queue.Queue()
        for _, row in df_map[[self.map_fields["URI"], self.map_fields["item_id"]]].iterrows():
            query = self.get_enrich_query(row[self.map_fields["URI"]])
            q.put((row[self.map_fields["item_id"]], query))

        if self.n_workers > 1:
            responses = self.parallel_queries(q, CSV)
        else:
            responses = self.sequential_queries(q, CSV)

        item_enriching = defaultdict(dict)
        for response in responses:
            idx, result = response
            df = pd.read_csv(BytesIO(result))

            if df.shape[0] > 1:
                print("At least one property has more than one value!")
                print(df.value_counts(dropna=False))

            item_enriching[idx] = df.iloc[0]  # getting pd.Series

        df_enrich = pd.DataFrame.from_dict(item_enriching, orient="index")
        df_enrich = df_enrich.rename(self.enrich_fields, axis=1)
        df_enrich.index.name = self.enrich_fields["item_id"]

        return df_enrich

    def get_enrich_query(self, URI) -> str:
        params = {"URI": URI}
        query = self.enrich_query_template.substitute(**params)
        return query


class MovieLens100k(MovieLens):
    """
    Dataset class for data integration between DBpedia and MovieLens-100k
    """

    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers)
        self.dataset_name = "MovieLens100k"

        self.item_separator = "|"
        self.user_separator = "|"
        self.rating_separator = "\t"
        self.item_fields = {
            "movie id": "item_id::string",
            "movie_title": "movie_title::string",
            "movie_year": "movie_year::string",  # extracted from movie_title
        }
        self.rating_fields = {
            "user id": "user_id::string",
            "item id": "item_id::string",
            "rating": "rating::number",
            "timestamp": "timestamp::number",
        }
        self.user_fields = {
            "user id": "user_id::string",
            "age": "age::string",
            "gender": "gender::string",
            "occupation": "occupation::string",
        }

    def load_item_data(self) -> pd.DataFrame():
        # Reading item file of MovieLens100k dataset
        filename = os.path.join(self.input_path, "u.item")
        column_names = """movie id | movie title | release date | video release date |
                    IMDb URL | unknown | Action | Adventure | Animation |
                    Children's | Comedy | Crime | Documentary | Drama | Fantasy |
                    Film-Noir | Horror | Musical | Mystery | Romance | Sci-Fi |
                    Thriller | War | Western"""
        column_names = [name.strip() for name in column_names.split("|")]
        df = pd.read_csv(
            filename,
            header=None,
            sep=self.item_separator,
            encoding="latin-1",
            names=column_names,
        )

        # Pre processing item
        # 1- Dropping unused fields
        df.set_index("movie id")
        df = df.drop(["video release date", "unknown", "IMDb URL"], axis=1)
        df = df.dropna()

        # 2- Extracting title and year
        df["movie_title"] = df["movie title"].apply(self._extract_title)
        df["movie_year"] = df["movie title"].apply(self._extract_year)

        df = df.rename(self.item_fields, axis=1)
        df = df[self.item_fields.values()]

        return df

    def load_user_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "u.user")
        column_names = "user id | age | gender | occupation | zip code"
        column_names = [name.strip() for name in column_names.split("|")]

        df = pd.read_csv(
            filename,
            header=None,
            sep=self.user_separator,
            encoding="latin-1",
            names=column_names,
        )
        df = df.rename(self.user_fields, axis=1)
        df = df[self.user_fields.values()]

        return df

    def load_rating_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "u.data")
        column_names = "user id | item id | rating | timestamp"
        column_names = [name.strip() for name in column_names.split("|")]

        df = pd.read_csv(
            filename,
            header=None,
            sep=self.rating_separator,
            encoding="latin-1",
            names=column_names,
        )
        df = df.rename(self.rating_fields, axis=1)
        df = df[self.rating_fields.values()]

        return df


class MovieLens1M(MovieLens):
    """
    Dataset class for data integration between DBpedia and MovieLens 1M
    """

    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers)
        self.dataset_name = "MovieLens1M"

        self.item_separator = "::"
        self.user_separator = "::"
        self.rating_separator = "::"
        self.item_fields = {
            "MovieID": "item_id::string",
            "movie_title": "movie_title::string",
            "movie_year": "movie_year::string",  # extracted from movie_title
        }
        self.rating_fields = {
            "UserID": "user_id::string",
            "MovieID": "item_id::string",
            "Rating": "rating::number",
            "Timestamp": "timestamp::number",
        }
        self.user_fields = {
            "UserID": "user_id::string",
            "Gender": "gender::string",
            "Age": "age::string",
            "Occupation": "occupation::string",
        }

    def load_item_data(self) -> pd.DataFrame():
        # Reading item file of MovieLens100k dataset
        filename = os.path.join(self.input_path, "movies.dat")
        column_names = "MovieID::Title::Genres"
        column_names = [name.strip() for name in column_names.split("::")]
        df = pd.read_csv(
            filename,
            header=None,
            sep=self.item_separator,
            encoding="latin-1",
            names=column_names,
            engine="python",
        )

        # Pre processing item
        # Extracting title and year
        df["movie_title"] = df["Title"].apply(self._extract_title)
        df["movie_year"] = df["Title"].apply(self._extract_year)

        df = df.rename(self.item_fields, axis=1)
        df = df[self.item_fields.values()]

        return df

    def load_user_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "users.dat")
        column_names = "UserID::Gender::Age::Occupation::Zip-code"
        column_names = [name.strip() for name in column_names.split("::")]

        df = pd.read_csv(
            filename,
            header=None,
            sep=self.user_separator,
            encoding="latin-1",
            names=column_names,
            engine="python",
        )

        df = df.rename(self.user_fields, axis=1)
        df = df[self.user_fields.values()]

        return df

    def load_rating_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "ratings.dat")
        column_names = "UserID::MovieID::Rating::Timestamp"
        column_names = [name.strip() for name in column_names.split("::")]

        df = pd.read_csv(
            filename,
            header=None,
            sep=self.rating_separator,
            encoding="latin-1",
            names=column_names,
            engine="python",
        )
        df = df.rename(self.rating_fields, axis=1)
        df = df[self.rating_fields.values()]

        return df
