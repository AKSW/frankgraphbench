import os
import pandas as pd
from string import Template
from SPARQLWrapper import SPARQLWrapper, JSON

class Dataset():
    def __init__(self, input_path, output_path):
        r"""
        Base class for Recommender System's datasets
        """
        self.input_path = input_path
        self.output_path = output_path

        self.sparql_endpoint = "http://dbpedia.org/sparql"

        # Output files
        self.item_filename = os.path.join(self.output_path, 'item.csv')
        self.user_filename = os.path.join(self.output_path, 'user.csv')
        self.rating_filename = os.path.join(self.output_path, 'rating.csv')
        self.map_filename = os.path.join(self.output_path, 'map.csv')

        # create output path if doesn't exist
        self.has_output_path()

        # The following variables need to be overwritten by the subclasses of Dataset()
        self.dataset_name = ''
        self.item_separator = '' 
        self.user_separator = ''
        self.rating_separator = ''

        # Chosen features to be extracted from dataset
        self.item_features = []
        self.user_features = []
        self.rating_features = []

        self.query_template = Template(None)


    def has_output_path(self):
        if not os.path.isdir(self.output_path):
            os.mkdir(self.output_path)
    
    def load_item_data(self) -> pd.DataFrame():
        """
        Loads item info of Dataset
        :return: returns pd.Dataframe() containing each item info.
        """
        raise NotImplementedError

    def load_user_data(self) -> pd.DataFrame():
        """
        Loads user info of Dataset
        :return: returns pd.Dataframe() containing each user info.
        """
        raise NotImplementedError

    def load_rating_data(self) -> pd.DataFrame():
        """
        Loads rating interactions of Dataset
        :return: returns pd.Dataframe() containing each rating interaction.
        """
        raise NotImplementedError
    
    def entity_linking(self, df_item) -> pd.DataFrame():
        """
        Entity link each item to their corresponding DBpedia's URI
        :return: returns pd.Dataframe() containing each movie id and their mapped URI 
        """
        raise NotImplementedError
    
    def get_query_params(self, *args, **kwargs) -> dict():
        """
        Returns query parameters to be substituted in the query template.
        :returns: returns dictionary to substitute query_template placeholders
        """
        raise NotImplementedError

    def query(self, params) -> dict():
        sparql_query = self.query_template.substitute(**params)
        sparql = SPARQLWrapper(self.sparql_endpoint)
        sparql.setQuery(sparql_query)
        sparql.setReturnFormat(JSON)

        try:
            return sparql.query().convert()
        except Exception as e:
            raise e
    
    def convert_item_data(self):
        """
        Converts loaded item data to a processed csv (item.csv).
        """
        try:
            print(f'Creating file: {self.item_filename}.')
            df_item = self.load_item_data()
            print(f'{df_item.shape[0]} items with {df_item.shape[1]} Fields')
            print('Fields: ' + ', '.join(self.item_fields))
            df_item.to_csv(self.item_filename, index=False)
        except NotImplementedError:
            print('Override load_item_data() method of your Dataset subclass.')
    
    def convert_user_data(self):
        """
        Converts loaded user data to a processed csv (user.csv). 
        """
        try:
            print(f'Creating file: {self.user_filename}')
            df_user = self.load_user_data()
            print(f'{df_user.shape[0]} users with {df_user.shape[1]} Fields')
            print('Fields: ' + ', '.join(self.user_fields))
            df_user.to_csv(self.user_filename, index=False)
        except NotImplementedError:
            print(f'Override load_user_data() of your Dataset subclass.')

    def convert_rating_data(self):
        """
        Converts loaded rating data to a processed csv (rating.csv)
        """
        try:
            print(f'Creating file: {self.rating_filename}')
            df_rating = self.load_rating_data()
            print(f'{df_rating.shape[0]} ratings with {df_rating.shape[1]} Fields')
            print('Fields: ' + ', '.join(self.rating_fields))
            df_rating.to_csv(self.rating_filename, index=False)
        except NotImplementedError:
            print(f'Override load_rating_data() of your Dataset subclass.')

    def map_URIs(self):
        """
        Maps each item to their corresponding DBpedia's URI.
        """
        try:
            df_item = pd.read_csv(self.item_filename)
            print(f'Mapping each dataset item with DBpedia: {self.map_filename}')
            df_map = self.entity_linking(df_item)
            df_map.to_csv(self.map_filename, index=False)
            
            # print mapping statistics
            n_items = df_map.shape[0]
            n_unmatched = df_map['URI'].isna().sum()
            print(f"{n_unmatched} items weren't matched, corresponding to {n_unmatched/n_items*100:.2f}% of a total of {n_items}.")
            

        except NotImplementedError:
            print('Override entity_linking() method of your Dataset subclass.')

    


        
        