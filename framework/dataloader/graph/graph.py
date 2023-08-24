from collections import defaultdict

from .node import *
from ...utils import get_optional_argument

import networkx as nx
import pandas as pd
from tqdm import tqdm
import numpy as np

"""
    Class wrapper on the top of a nx.Graph
"""
class Graph(nx.Graph):
    def __init__(self, name, item, user, ratings, enrich = None):
        super().__init__()
        self.name = name 
        self.item_nodes = [] # it is really necessary? O(n) removing nodes
        self.user_nodes = []
        self.rating_edges = defaultdict(list)       # user: [items]
        self.rating_item2users = defaultdict(list)   # item: [users]
        
        # Adding item nodes and properties nodes
        self._add_item_info(item, enrich)
        self._add_user_info(user)
        self._add_ratings(ratings)

    def info(self):
        n_nodes = self.number_of_nodes()
        n_edges = self.number_of_edges()
        message =  f'{self.name} graph with a total of {n_nodes} nodes and {n_edges} edges'
        return message

    def get_item_nodes(self) -> [ItemNode]:
        return self.item_nodes

    def get_user_nodes(self) -> [UserNode]:
        return self.user_nodes

    def get_rating_edges(self) -> tuple:
        for user, items in self.rating_edges.items():
            for item in items:
                yield (user, item)
    
    def get_ratings_with_labels(self):
        edges, labels = [], []
        for (u,v) in list(self.get_rating_edges()):
            data = self.get_edge_data(u,v)
            edges.append((u.get_id(), v.get_id()))
            labels.append(data['rating'])

        return np.array(edges), np.array(labels)
    
    def add_node(self, node_for_adding: Node, **attr):
        super().add_node(node_for_adding, **attr)
        if isinstance(node_for_adding, ItemNode):
            self.item_nodes.append(node_for_adding)
        elif isinstance(node_for_adding, UserNode):
            self.user_nodes.append(node_for_adding)
    
    def add_edge(self, u_of_edge, v_of_edge, **attr):
        super().add_edge(u_of_edge, v_of_edge, **attr)
        data = self.get_edge_data(u_of_edge, v_of_edge, default={})
        edge_type = data.get('type')

        if edge_type == 'rated':
            self.rating_edges[u_of_edge].append(v_of_edge)
            self.rating_item2users[v_of_edge].append(u_of_edge)
            
    
    def remove_edge(self, u, v):
        if isinstance(u, UserNode) and isinstance(v, ItemNode):
            self.rating_edges[u].remove(v)
            self.rating_item2users[v].remove(u)

        return super().remove_edge(u, v)
    
    def remove_node(self, n):
        super().remove_node(n)
        if isinstance(n, ItemNode):
            self.item_nodes.remove(n)
            del self.rating_item2users[n]
            for user, items in self.rating_edges.items():
                if n in items:
                    self.rating_edges[user].remove(n)
        elif isinstance(n, UserNode):
            self.user_nodes.remove(n)
            del self.rating_edges[n]
            for item, users in self.rating_item2users.items():
                if n in users:
                    self.rating_item2users[item].remove(n)

    def _add_item_info(self, item, enrich):
        # Extracting info from .csv
        df_item = pd.read_csv(item['path'])
        extra_features = get_optional_argument(item, 'extra_features', [])
        df_item = df_item[['item_id'] + extra_features]
        if enrich is not None:
            # Merging info from original dataset and enriched 
            df_map = pd.read_csv(enrich['map_path'])
            df_item = pd.merge(df_item, df_map, on="item_id", how="left")  
            if enrich['remove_unmatched']:
                df_item = df_item[df_item['URI'].notna()]
            
            df_enriched = self._get_enrich_dataframe(**enrich)
            df_item = pd.merge(df_item, df_enriched, on='item_id', how="left")

        # Creating graph from dataframe
        desc = 'Adding item info into network'
        n_items = df_item.shape[0]
        properties = list(df_item.columns)
        properties.remove('item_id')

        # Adding item nodes and properties nodes
        for _, row in tqdm(df_item.iterrows(), total=n_items, desc=desc):
            item_node = ItemNode(row['item_id'])
            self.add_node(item_node)

            for property_ in properties:
                self._add_node_property(item_node, row, property_)
    
    def _add_node_property(self, source: Node, row: pd.Series, property_: str):
        prop_value = row[property_]
        if not isinstance(prop_value, list) and pd.notna(prop_value):
            # Single property_
            property_node = PropertyNode(row[property_], property_)
            self.add_edge(source, property_node, type='has_property')
        elif isinstance(prop_value, list):
            # Multiples properties
            for value in row[property_]:
                property_node = PropertyNode(value, property_)
                self.add_edge(source, property_node, type='has_property')


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
        extra_features = get_optional_argument(user, 'extra_features', [])
        df_user = df_user[['user_id'] + extra_features]

        total_users = df_user.shape[0]
        desc = 'Adding user info into network'
        properties = list(df_user.columns)
        properties.remove('user_id')

        for _, row in tqdm(df_user.iterrows(), total=total_users, desc=desc):
            user_node = UserNode(row['user_id'])
            self.add_node(user_node)

            for property_ in properties:
                self._add_node_property(user_node, row, property_)

    def _add_ratings(self, ratings):
        df_ratings = pd.read_csv(ratings['path'])
        total_ratings = df_ratings.shape[0]
        desc = 'Adding ratings into network'

        for _, row in tqdm(df_ratings.iterrows(), total=total_ratings, desc=desc):
            item_node = ItemNode(row['item_id'])
            user_node = UserNode(row['user_id'])

            if item_node in self and user_node in self:
                attrs = {'type': 'rated', 'rating': row['rating']}
                if ratings['timestamp']:
                    attrs['timestamp'] = row['timestamp']

                self.add_edge(user_node, item_node, **attrs)