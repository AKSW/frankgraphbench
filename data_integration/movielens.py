import os
import re
import queue
from string import Template
from .dataset import Dataset

import pandas as pd
from tqdm import tqdm
from thefuzz import process


class MovieLens(Dataset):
    """
    General MovieLens(Dataset) class for data integration between DBpedia and MovieLens
    """
    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers)
        self.query_template = Template('''
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
        ''')
    
    def _extract_title(self, title):
        regex = re.compile(r'\((\d{4})\)')
        rgx_match = regex.search(title)
        year_start, _ = rgx_match.span()
        movie_title = title[:year_start-1].strip() 

        # removing parenthesis (name of the film in other languages)
        movie_title = [s.split(')')[-1] for s in movie_title.split('(')][0]

        # Reversing titles with X, The
        movie_title = movie_title.split(',')
        movie_title = [movie_title[-1].strip()] + [title.strip() for title in movie_title[:-1]]
        movie_title = ' '.join(movie_title)
        
        movie_title = movie_title.strip()
        return movie_title

    def _extract_year(self, title):
        regex = re.compile(r'\((\d{4})\)')
        rgx_match = regex.search(title)
        movie_year = rgx_match.group()
        movie_year = int(movie_year[1:-1])
        return movie_year

    def entity_linking(self, df_item) -> pd.DataFrame():
        q = queue.Queue()
        for idx, row in df_item[['movie_title', 'movie_year']].iterrows():
            params = self.get_query_params(row['movie_title'], row['movie_year'])
            q.put((idx, params))

        if self.n_workers > 1:
            responses = self.parallel_queries(q)
        else:
            responses = self.sequential_queries(q)
        
        URI_mapping = {}
        for response in tqdm(responses, desc='Disambiguating query return'):
            candidate_URIs = []
            idx, result = response
            for binding in result['results']['bindings']:
                URI = binding['film']['value']
                candidate_URIs.append(URI)
                
            expected_URI = f"http://dbpedia.org/resource/{df_item.iloc[idx]['movie_title']}"
            str_matching_result = process.extractOne(expected_URI, candidate_URIs)
            
            if str_matching_result is not None:
                URI, _ = str_matching_result
                URI_mapping[idx] = URI
        
        df_map = pd.DataFrame({'item_id': df_item['item_id']})
        df_map.set_index('item_id')
        df_map['URI'] = pd.Series(URI_mapping)

        return df_map

    def get_query_params(self, title, year) -> dict():
        title = title.translate(self._special_chars_map)
        title = title.replace(' ', '.*')
        title = '^' + title
        return {'name_regex': title, 'year_category': f'dbr:Category:{str(year)}_films'}
    


class MovieLens100k(MovieLens):
    """
    Dataset class for data integration between DBpedia and MovieLens-100k
    """
    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers)
        self.dataset_name = 'MovieLens100k'

        self.item_separator = '|'
        self.user_separator = '|'
        self.rating_separator = '\t'

        self.item_fields = ['item_id', 'movie_title', 'movie_year']
        self.user_fields = ['user_id', 'age', 'gender', 'occupation']
        self.rating_fields = ['user_id', 'item_id', 'rating', 'timestamp']
        self.map_fields = ['item_id', 'URI']

    def load_item_data(self) -> pd.DataFrame():
        # Reading item file of MovieLens100k dataset
        filename = os.path.join(self.input_path, 'u.item')
        column_names = '''movie id | movie title | release date | video release date |
                    IMDb URL | unknown | Action | Adventure | Animation |
                    Children's | Comedy | Crime | Documentary | Drama | Fantasy |
                    Film-Noir | Horror | Musical | Mystery | Romance | Sci-Fi |
                    Thriller | War | Western'''
        column_names = [name.strip() for name in column_names.split('|')]
        df = pd.read_csv(
            filename, header=None, sep=self.item_separator,
            encoding='latin-1', names=column_names
        )

        # Pre processing item
        # 1- Dropping unused fields
        df.set_index('movie id')
        df = df.drop(['video release date', 'unknown', 'IMDb URL'], axis=1)
        df = df.dropna()
        
        # 2- Extracting title and year
        df['movie_title'] = df['movie title'].apply(self._extract_title)
        df['movie_year'] = df['movie title'].apply(self._extract_year)
        df['item_id'] = df['movie id']
        
        df = df[self.item_fields]

        return df
        
    def load_user_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, 'u.user')
        column_names = 'user id | age | gender | occupation | zip code'
        column_names = [name.strip() for name in column_names.split('|')]

        df = pd.read_csv(
            filename, header=None, sep=self.user_separator,
            encoding='latin-1', names=column_names
        )
        # Removing zip code
        df = df.drop(['zip code'], axis=1)
        df.columns = self.user_fields

        return df


    def load_rating_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, 'u.data')
        column_names = 'user id | item id | rating | timestamp'
        column_names = [name.strip() for name in column_names.split('|')]

        df = pd.read_csv(
            filename, header=None, sep=self.rating_separator,
            encoding='latin-1', names=column_names
        )
        # Will use all fields provided by the dataset
        # renaming columns
        df.columns = self.rating_fields

        return df
    

class MovieLens1M(MovieLens):
    """
    Dataset class for data integration between DBpedia and MovieLens 1M
    """
    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers)
        self.dataset_name = 'MovieLens1M'

        self.item_separator = '::'
        self.user_separator = '::'
        self.rating_separator = '::'

        self.item_fields = ['item_id', 'movie_title', 'movie_year']
        self.user_fields = ['user_id', 'gender', 'age', 'occupation']
        self.rating_fields = ['user_id', 'item_id', 'rating', 'timestamp']
        self.map_fields = ['item_id', 'URI']
    
    def load_item_data(self) -> pd.DataFrame():
        # Reading item file of MovieLens100k dataset
        filename = os.path.join(self.input_path, 'movies.dat')
        column_names = 'MovieID::Title::Genres'
        column_names = [name.strip() for name in column_names.split('::')]
        df = pd.read_csv(
            filename, header=None, sep=self.item_separator,
            encoding='latin-1', names=column_names, engine='python'
        )

        # Pre processing item       
        # Extracting title and year
        df['movie_title'] = df['Title'].apply(self._extract_title)
        df['movie_year'] = df['Title'].apply(self._extract_year)
        df['item_id'] = df['MovieID']
        
        df = df[self.item_fields]

        return df

    def load_user_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, 'users.dat')
        column_names = 'UserID::Gender::Age::Occupation::Zip-code'
        column_names = [name.strip() for name in column_names.split('::')]

        df = pd.read_csv(
            filename, header=None, sep=self.user_separator,
            encoding='latin-1', names=column_names, engine='python'
        )
        # Removing zip code
        df = df.drop('Zip-code', axis=1)
        df.columns = self.user_fields

        return df

    def load_rating_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, 'ratings.dat')
        column_names = 'UserID::MovieID::Rating::Timestamp'
        column_names = [name.strip() for name in column_names.split('::')]

        df = pd.read_csv(
            filename, header=None, sep=self.rating_separator,
            encoding='latin-1', names=column_names, engine='python'
        )
        # Will use all fields provided by the dataset
        # renaming columns
        df.columns = self.rating_fields

        return df
        