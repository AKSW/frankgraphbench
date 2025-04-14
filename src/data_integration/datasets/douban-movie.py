import os
import re
import queue
from io import BytesIO
from collections import defaultdict

from tqdm import tqdm
from thefuzz import process
from SPARQLWrapper import CSV
import pandas as pd
from string import Template

from ..dataset import Dataset

class DoubanMovie(Dataset):
    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers)
        self.dataset_name = "Douban Movie Short"

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
                    ?film rdfs:label ?label .
                    FILTER regex(?label, "$name_regex", "i")
                }
                UNION
                {
                    ?film rdf:type dbo:Film .
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

        self.item_fields_extract = ["Movie_Name_EN", "Movie_Name_CN"]
        self.user_fields_extract = ["Username"]
        self.rating_fields_extract = ["ID", "Date", "Star", "Comment", "Like", "Movie_Name_EN", "Username"]

        self.map_fields = {"item_id": "item_id::string", "URI": "URI::string"}

        self.item_fields = {
            "movie_id": "item_id::string",
            "Movie_Name_EN": "name_EN::string",
            "Movie_Name_CN": "name_CN::string"
        }

        self.user_fields = {
            "user_id": "user_id::string",
            "Username": "name::string"
        }

        self.rating_fields = {
            "user_id": "user_id::string",
            "movie_id": "item_id::string",
            "Star": "rating::number",
            "Date": "date::string",
            "Comment": "comment::string",
            "Like": "like_count::number"
        }

    def entity_linking(self, df_item) -> pd.DataFrame():
        q = queue.Queue()
        for idx, row in df_item[["name_EN", "item_id"]].iterrows():
            query = self.get_map_query(row["name_EN"])
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

            expected_URI = f"http://dbpedia.org/resource/{df_item.loc[df_item.item_id == idx]['name_EN']}"
            str_matching_result = process.extractOne(expected_URI, candidate_URIs)

            if str_matching_result is not None:
                URI, _ = str_matching_result
                URI_mapping[idx] = URI

        df_map = pd.DataFrame({"item_id": df_item["item_id"]})
        df_map.set_index("item_id")
        df_map["URI"] = df_map["item_id"].apply(lambda id: URI_mapping.get(id))
        df_map = df_map.rename(self.map_fields, axis=1)

        return df_map

    def get_map_query(self, title) -> str:
        # title = title.translate(self._special_chars_map)
        title = title.replace(" ", ".*")
        title = "^" + title

        params = {
            "name_regex": title,
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

    def load_item_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "DMSC.csv")
        df = pd.read_csv(filename)
        
        df = df[self.item_fields_extract].drop_duplicates().reset_index(drop=True)
        df['movie_id'] = df.index

        df = df.rename(self.item_fields, axis=1)
        df = df[self.item_fields.values()]
        return df
    
    def load_user_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "DMSC.csv")
        df = pd.read_csv(filename)
        
        df = df[self.user_fields_extract].drop_duplicates().reset_index(drop=True)
        df['user_id'] = df.index

        df = df.rename(self.user_fields, axis=1)
        df = df[self.user_fields.values()]
        return df
    
    def load_rating_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "DMSC.csv")
        df = pd.read_csv(filename)

        item_df = df[self.item_fields_extract].drop_duplicates().reset_index(drop=True)
        item_df['movie_id'] = item_df.index

        user_df = df[self.user_fields_extract].drop_duplicates().reset_index(drop=True)
        user_df['user_id'] = user_df.index
        
        df = df[self.rating_fields_extract].drop_duplicates().reset_index(drop=True)
        
        df = df.join(item_df.set_index('Movie_Name_EN'), on='Movie_Name_EN')
        df = df.join(user_df.set_index('Username'), on='Username')

        df = df.rename(self.rating_fields, axis=1)
        df = df[self.rating_fields.values()]
        return df

