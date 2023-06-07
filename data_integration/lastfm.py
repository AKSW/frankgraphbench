import os
import re
from string import Template
from .dataset import Dataset

import pandas as pd
from tqdm import tqdm
from thefuzz import process

class LastFM(Dataset):
    def __init__(self, input_path, output_path):
        super().__init__(input_path, output_path)
        self.dataset_name = 'LastFM'

        self.item_separator = '\t'
        # self.user_separator = '|'
        # self.rating_separator = '\t'

        self.item_fields = ['item_id', 'name']
        # self.user_fields = ['user_id', 'age', 'gender', 'occupation']
        # self.rating_fields = ['user_id', 'item_id', 'rating', 'timestamp']
        # self.map_fields = ['item_id', 'URI']

        self.query_template = Template('''
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
                    ?artist rdf:type dbo:Band .
                    ?artist rdfs:label ?label .
                    FILTER regex(?label, "$name_regex", "i")
                }
            }
        ''')
        # self.query_template = Template('''
        #     PREFIX dct:  <http://purl.org/dc/terms/>
        #     PREFIX dbo:  <http://dbpedia.org/ontology/>
        #     PREFIX dbr:  <http://dbpedia.org/resource/>
        #     PREFIX rdf:	 <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        #     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        #     SELECT DISTINCT ?artist WHERE {
        #         {
        #             ?artist rdf:type dbo:MusicalArtist .
        #             ?artist rdfs:label ?label .
        #             FILTER regex(?label, "$name_regex", "i")
        #         }
        #         UNION
        #         {
        #             ?artist rdf:type dbo:MusicalArtist .
        #             ?tmp dbo:wikiPageRedirects ?artist .
        #             ?tmp rdfs:label ?label .
        #             FILTER regex(?label, "$name_regex", "i") .
        #         }
        #         UNION
        #         {
        #             ?artist rdf:type dbo:Band .
        #             ?artist rdfs:label ?label .
        #             FILTER regex(?label, "$name_regex", "i")
        #         }
        #         UNION
        #         {
        #             ?artist rdf:type dbo:Band .
        #             ?tmp dbo:wikiPageRedirects ?artist .
        #             ?tmp rdfs:label ?label .
        #             FILTER regex(?label, "$name_regex", "i") .
        #         }
        #     }
        # ''')


    def load_item_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, 'artists.dat')
        columns = ['id','name','url','pictureURL']

        df = pd.read_csv(filename, sep=self.item_separator)
        df = df.drop(columns[2:], axis=1) # Will not use url and picture URL
        df.columns = self.item_fields
        return df

    def entity_linking(self, df_item) -> pd.DataFrame():
        URI_mapping = {}
        n_iters = df_item.shape[0]
        for idx, row in tqdm(df_item[['name']].iterrows(), total=n_iters):
            try:
                params = self.get_query_params(row['name'])
                result = self.query(params)
                candidate_URIs = []
                for binding in result['results']['bindings']:
                    URI = binding['artist']['value']
                    candidate_URIs.append(URI)
                
                print(candidate_URIs)
                expected_URI = f'http://dbpedia.org/resource/{row["name"]}'
                str_matching_result = process.extractOne(expected_URI, candidate_URIs)

                if str_matching_result is not None:
                    URI, _ = str_matching_result
                    URI_mapping[idx] = URI
                    print(URI)

            except Exception as e:
                print(f'Error while matching {row["name"]}:')
                print(e)
        
        df_map = pd.DataFrame({'item_id': df_item['item_id']})
        df_map.set_index('item_id')
        df_map['URI'] = pd.Series(URI_mapping)

        return df_map
    
    def get_query_params(self, name) -> dict():
        name = name.replace(' ', '.*')
        return {'name_regex': name}
    