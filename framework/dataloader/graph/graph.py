import os

from .node import *

import networkx as nx
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt

"""
    Class wrapper on the top of a nx.Graph
"""
class Graph():
    def __init__(self, name, item, user, ratings, enrich = None):
        self.graph = nx.Graph()
        self.name = name 

        
        # Adding item nodes and properties nodes
        self._add_item_info(item, enrich)
        self._add_user_info(user)
        self._add_ratings(ratings)

        print(self.graph[UserNode(1)])
        print(self.graph[ItemNode(1)])



    def to_network(self):
        return self.graph

    def _add_item_info(self, item, enrich):
        # Extracting info from .csv
        df_item = pd.read_csv(item['path'])
        extra_features = self._get_optional_argument(item, 'extra_faetures', [])
        df_item = df_item[['item_id'] + extra_features]
        if enrich is not None:
            # Merging info from original dataset and enriched 
            df_map = pd.read_csv(enrich['map_path'])
            df_item = pd.merge(df_item, df_map, on="item_id", how="left")  
            if enrich['remove_unmatched']:
                df_item = df_item[df_item['URI'].notna()]
            
            df_enriched = self._get_enrich_dataframe(**enrich)
            df_item = pd.merge(df_item, df_enriched, on='item_id')

        # Creating graph from dataframe
        desc = 'Adding item info into network'
        n_items = df_item.shape[0]
        properties = list(df_item.columns)
        properties.remove('item_id')

        # Adding item nodes and properties nodes
        for _, row in tqdm(df_item.iterrows(), total=n_items, desc=desc):
            item_node = ItemNode(row['item_id'])
            self.graph.add_node(item_node)

            for property_ in properties:
                self._add_node_property(item_node, row, property_)
    
    def _add_node_property(self, source: Node, row: pd.Series, property_: str):
        prop_value = row[property_]
        if not isinstance(prop_value, list) and pd.notna(prop_value):
            # Single property_
            property_node = PropertyNode(row[property_], property_)
            self.graph.add_edge(source, property_node, type=property_)
        elif isinstance(prop_value, list):
            # Multiples properties
            for value in row[property_]:
                property_node = PropertyNode(value, property_)
                self.graph.add_edge(source, property_node, type=property_)


    def _get_optional_argument(self, config, key, default):
        try:
            return config[key]
        except KeyError:
            return default
    
    def _get_enrich_dataframe(self, **enrich_config):
        df = pd.read_csv(enrich_config['enrich_path'])
        df_enriched = pd.DataFrame(df.copy()['item_id'])

        for property in enrich_config['properties']:
            prop_type = property['type']
            grouped = property['grouped']
            sep = property.get('sep')

            prop_series = df[prop_type]
            f = lambda x: x.split(sep) if grouped and pd.notna(x) else x
            df_enriched[prop_type] = prop_series.apply(f)

        return df_enriched

    def _add_user_info(self, user):
        df_user = pd.read_csv(user['path'])
        extra_features = self._get_optional_argument(user, 'extra_features', [])
        df_user = df_user[['user_id'] + extra_features]

        total_users = df_user.shape[0]
        desc = 'Adding user info into network'
        properties = list(df_user.columns)
        properties.remove('user_id')

        for _, row in tqdm(df_user.iterrows(), total=total_users, desc=desc):
            user_node = UserNode(row['user_id'])
            self.graph.add_node(user_node)

            for property_ in properties:
                self._add_node_property(user_node, row, property_)

    def _add_ratings(self, ratings):
        df_ratings = pd.read_csv(ratings['path'])
        total_ratings = df_ratings.shape[0]
        desc = 'Adding ratings into network'

        for _, row in tqdm(df_ratings.iterrows(), total=total_ratings, desc=desc):
            item_node = ItemNode(row['item_id'])
            user_node = UserNode(row['user_id'])
            if ratings['timestamp']:
                self.graph.add_edge(item_node, user_node, timestamp=row['timestamp'])
            else:
                self.graph.add_edge(item_node, user_node)


        
    
    # def _add_items(self, **items_config):
    #     df = pd.read_csv(items_config['path']) 
    #     n_items = df.shape[0]
    #     desc = 'Adding item nodes and their original dataset features'

    #     for _, row in tqdm(df.head(40).iterrows(), total=n_items, desc=desc):
    #         item_node = ItemNode(row['item_id'])
    #         self.graph.add_node(item_node)

    #         for feature in items_config['extra_features']:
    #             feat_node = PropertyNode(row[feature], feature)
    #             self.graph.add_edge(item_node, feat_node, type=feature)

    # def _add_enrich(self, **enrich_config):
    #     df = pd.read_csv(enrich_config['map_path'])
    #     # if enrich_config['remove_unmatched']:
    #     #     df = df[df['URI'].notna()]
        
    #     n_items = df.shape[0]
    #     desc = 'Adding edges between item_id and URI'

    #     for _, row in tqdm(df.head(40).iterrows(), total=n_items, desc=desc):
    #         item = ItemNode(row['item_id'])
    #         uri = row['URI']
    #         if not pd.isna(uri):
    #             uri = PropertyNode(uri, 'URI')
    #             self.graph.add_edge(item, uri, type='uri')
    #         else:
    #             self.graph.add_node(item)


        
        


        
