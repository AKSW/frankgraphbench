import os
import re
import queue
from string import Template
from .dataset import Dataset

import pandas as pd
from tqdm import tqdm
from thefuzz import process

class Steam(Dataset):
    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers)
        self.dataset_name = 'Steam'

        self.item_separator = ','
        # self.user_separator = '|'
        # self.rating_separator = '\t'

        self.item_fields = ['item_id', 'title', 'date_release']
        # self.user_fields = ['user_id', 'age', 'gender', 'occupation']
        # self.rating_fields = ['user_id', 'item_id', 'rating']
        # self.map_fields = ['item_id', 'URI']

        self.map_query_template = Template('''
            PREFIX dct:  <http://purl.org/dc/terms/>
            PREFIX dbo:  <http://dbpedia.org/ontology/>
            PREFIX dbr:  <http://dbpedia.org/resource/>
            PREFIX rdf:	 <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?game WHERE {
                {
                    ?game rdf:type dbo:VideoGame .
                    ?game rdfs:label ?label .
                    FILTER regex(?label, "$name_regex", "i")
                }
                UNION
                {
                    ?game rdf:type dbo:VideoGame .
                    ?tmp dbo:wikiPageRedirects ?game .
                    ?tmp rdfs:label ?label .
                    FILTER regex(?label, "$name_regex", "i") .
                }
            }
        ''')

    def load_item_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, 'steam_games.csv')
        used_columns = ['app_id', 'title', 'date_release']

        df = pd.read_csv(filename, sep=self.item_separator)
        df = df[used_columns]
        df.columns = self.item_fields

        return df 

    def entity_linking(self, df_item) -> pd.DataFrame():
        q = queue.Queue()
        for idx, row in df_item[['title']].iterrows():
            query = self.get_map_query(row['title'])
            q.put((idx, query))
        
        if self.n_workers > 1:
            responses = self.parallel_queries(q)
        else:
            responses = self.sequential_queries(q)

        URI_mapping = {}
        for response in tqdm(responses, desc='Disambiguating query return'):
            candidate_URIs = []
            idx, result = response
            for binding in result['results']['bindings']:
                URI = binding['game']['value']
                candidate_URIs.append(URI)
            
            expected_URI = f'http://dbpedia.org/resource/{df_item.iloc[idx]["title"]}'
            str_matching_result = process.extractOne(expected_URI, candidate_URIs)

            if str_matching_result is not None:
                URI, _ = str_matching_result
                URI_mapping[idx] = URI

        df_map = pd.DataFrame({'item_id': df_item['item_id']})
        df_map.set_index('item_id')
        df_map['URI'] = pd.Series(URI_mapping)

        return df_map

    def get_map_query(self, title) -> str:
        title = title.encode('ascii', 'ignore').decode()
        title = title.translate(self._special_chars_map)
        title = title.replace(' ', '.*')
        title = '^' + title + '$'

        params = {'name_regex': title}
        query = self.map_query_template.substitute(**params)
        return query

