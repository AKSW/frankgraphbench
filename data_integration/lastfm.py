import os
import re
import queue
from string import Template
from .dataset import Dataset
from .worker import Worker

import pandas as pd
from tqdm import tqdm
from thefuzz import process

class LastFM(Dataset):
    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers)
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
        q = queue.Queue()
        for idx, row in df_item[['name']].iterrows():
            params = self.get_query_params(row['name'])
            q.put((idx, params))
        
        responses = self.parallel_queries(q)
        
        URI_mapping = {}
        for response in tqdm(responses, desc='Disambiguating query return'):
            candidate_URIs = []
            idx, result = response
            for binding in result['results']['bindings']:
                URI = binding['artist']['value']
                candidate_URIs.append(URI)
            
            expected_URI = f'http://dbpedia.org/resource/{row["name"]}'
            str_matching_result = process.extractOne(expected_URI, candidate_URIs)

            if str_matching_result is not None:
                URI, _ = str_matching_result
                URI_mapping[idx] = URI

        df_map = pd.DataFrame({'item_id': df_item['item_id']})
        df_map.set_index('item_id')
        df_map['URI'] = pd.Series(URI_mapping)

        return df_map
    
    def get_query_params(self, name) -> dict():
        # name = '.*'.join([re.escape(x) for x in name.split(' ')])
        name = name.replace(' ', '.*')
        name = '^' + name
        return {'name_regex': name}
    