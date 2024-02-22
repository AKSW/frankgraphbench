import os
import re
import queue
from string import Template
from ..dataset import Dataset

from io import BytesIO
from collections import defaultdict


import pandas as pd
from tqdm import tqdm
from thefuzz import process
from SPARQLWrapper import CSV


class LastFM(Dataset):
    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers)
        self.dataset_name = "LastFM"

        self.item_separator = "\t"
        # self.user_separator = '|'
        self.rating_separator = "\t"
        self.social_separator = "\t"

        self.item_fields = {"id": "item_id::string", "name": "name::string"}
        self.user_fields = {"userID": "user_id::string"}
        self.rating_fields = {
            "userID": "user_id::string",
            "artistID": "item_id::string",
            "weight": "rating::number",
        }
        self.map_fields = {"item_id": "item_id::string", "URI": "URI::string"}
        self.social_fields = {"userID": "user1::string", "friendID": "user2::string"}

        self.map_query_template = Template(
            """
            PREFIX dct:  <http://purl.org/dc/terms/>
            PREFIX dbo:  <http://dbpedia.org/ontology/>
            PREFIX dbr:  <http://dbpedia.org/resource/>
            PREFIX rdf:	 <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?artist WHERE {
                {
                    ?artist rdf:type dbo:MusicalArtist .
                    ?artist rdfs:label ?label .
                    FILTER regex(?label, "$name_regex", "i")
                }
                UNION
                {
                    ?artist rdf:type dbo:MusicalArtist .
                    ?tmp dbo:wikiPageRedirects ?artist .
                    ?tmp rdfs:label ?label .
                    FILTER regex(?label, "$name_regex", "i") .
                }
                UNION
                {
                    ?artist rdf:type dbo:Band .
                    ?artist rdfs:label ?label .
                    FILTER regex(?label, "$name_regex", "i")
                }
                UNION
                {
                    ?artist rdf:type dbo:Band .
                    ?tmp dbo:wikiPageRedirects ?artist .
                    ?tmp rdfs:label ?label .
                    FILTER regex(?label, "$name_regex", "i") .
                }
            }
        """
        )

        self.enrich_query_template = Template(
            """
            PREFIX dct:  <http://purl.org/dc/terms/>
            PREFIX dbo:  <http://dbpedia.org/ontology/>
            PREFIX dbr:  <http://dbpedia.org/resource/>
            PREFIX rdf:	 <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT
                ?abstract
                (GROUP_CONCAT(DISTINCT ?bandMember; SEPARATOR="::") AS ?bandMember)
                (GROUP_CONCAT(DISTINCT ?genre; SEPARATOR="::") AS ?genre)
                (GROUP_CONCAT(DISTINCT ?associatedMusicalArtist; SEPARATOR="::") AS ?associatedMusicalArtist)
                (GROUP_CONCAT(DISTINCT ?awards; SEPARATOR="::") AS ?awards)
                (GROUP_CONCAT(DISTINCT ?recordLabel; SEPARATOR="::") AS ?recordLabel)
                (GROUP_CONCAT(DISTINCT ?associatedBand; SEPARATOR="::") AS ?associatedBand)
                (GROUP_CONCAT(DISTINCT ?origin; SEPARATOR="::") AS ?origin)
            WHERE {
                OPTIONAL { <$URI>   dbo:genre           ?genre              }   .
                OPTIONAL { <$URI>   dbo:abstract        ?abstract           }   .
                OPTIONAL { <$URI>   dbp:origin          ?origin             }   .
                OPTIONAL { <$URI>   dbo:recordLabel     ?recordLabel        }   .
                OPTIONAL { <$URI>   dbo:bandMember     ?bandMember        }   .
                OPTIONAL { <$URI>   dbo:associatedMusicalArtist     ?associatedMusicalArtist        }   .
                OPTIONAL { <$URI>   dbo:associatedBand     ?associatedBand        }   .
                OPTIONAL { <$URI>   dbp:awards     ?awards        }   .
                                              
                FILTER(LANG(?abstract) = 'en')
            }
        """
        )

    def load_item_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "artists.dat")

        df = pd.read_csv(filename, sep=self.item_separator)
        df = df.rename(self.item_fields, axis=1)
        df = df[self.item_fields.values()]
        return df

    def entity_linking(self, df_item) -> pd.DataFrame():
        q = queue.Queue()
        for idx, row in df_item[["name", "item_id"]].iterrows():
            query = self.get_map_query(row["name"])
            q.put((row["item_id"], query))

        if self.n_workers > 1:
            responses = self.parallel_queries(q)
        else:
            responses = self.sequential_queries(q)

        URI_mapping = {}
        for response in tqdm(responses, desc="Disambiguating query return"):
            candidate_URIs = []
            idx, result = response
            for binding in result["results"]["bindings"]:
                URI = binding["artist"]["value"]
                candidate_URIs.append(URI)

            expected_URI = f'http://dbpedia.org/resource/{df_item.loc[df_item.item_id == idx]["name"]}'
            str_matching_result = process.extractOne(expected_URI, candidate_URIs)

            if str_matching_result is not None:
                URI, _ = str_matching_result
                URI_mapping[idx] = URI

        df_map = pd.DataFrame({"item_id": df_item["item_id"]})
        df_map.set_index("item_id")
        df_map["URI"] = df_map["item_id"].apply(lambda id: URI_mapping.get(id))
        df_map = df_map.rename(self.map_fields, axis=1)

        return df_map

    def get_map_query(self, name) -> str:
        name = name.translate(self._special_chars_map)
        name = name.replace(" ", ".*")
        name = "^" + name
        name = name + "$"

        params = {"name_regex": name}
        query = self.map_query_template.substitute(**params)
        return query

    def enrich(self, df_map):
        df_map = df_map[df_map["URI"].notna()]

        q = queue.Queue()
        for _, row in df_map[["URI", "item_id"]].iterrows():
            query = self.get_enrich_query(row["URI"])
            q.put((row["item_id"], query))

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
        df_enrich.index.name = "item_id"

        return df_enrich

    def get_enrich_query(self, URI) -> str:
        params = {"URI": URI}
        query = self.enrich_query_template.substitute(**params)
        return query

    def load_rating_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "user_artists.dat")
        df = pd.read_csv(filename, sep=self.rating_separator)
        df = df.rename(self.rating_fields, axis=1)
        df = df[self.rating_fields.values()]

        return df

    def load_social_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "user_friends.dat")
        df = pd.read_csv(filename, sep=self.social_separator)
        df = df.rename(self.social_fields, axis=1)
        df = df[self.social_fields.values()]

        return df

    def load_user_data(self) -> pd.DataFrame():
        # There is no .dat only for user (none aditional user info)
        # Will extract the users from the rating data
        filename = os.path.join(self.input_path, "user_artists.dat")
        df = pd.read_csv(filename, sep=self.rating_separator)
        users = df["userID"].unique()
        df = df.rename(self.user_fields)
        df = pd.DataFrame(pd.Series(users), columns=self.user_fields.values())

        return df
