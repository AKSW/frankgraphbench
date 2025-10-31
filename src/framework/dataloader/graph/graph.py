from collections import defaultdict

from .node import *
from ...utils import get_optional_argument

import networkx as nx
import pandas as pd
from tqdm import tqdm
import numpy as np

from typing import Set, Tuple, Dict

"""
    Class wrapper on the top of a nx.Graph
"""


class Graph(nx.Graph):

    def __init__(self):
        super().__init__()
        self.datatype_separator = "::"
        self.item_nodes = set()
        self.user_nodes = set()
        self.rating_edges = defaultdict(set)  # { user: Set([items]) }
        self.rating_item2users = defaultdict(set)  # { item: Set([users]) }

    def build(self, name, item, user, ratings, enrich=None, social=None):
        # Adding item, user and properties nodes
        self.name = name
        self._add_item_info(item, enrich)
        self._add_user_info(user)
        self._add_ratings(ratings)
        if social is not None:
            self._add_social_links(social)

    def info(self):
        n_nodes = self.number_of_nodes()
        n_edges = self.number_of_edges()
        message = (
            f"{self.name} graph with a total of {n_nodes} nodes and {n_edges} edges"
        )
        message += f" ({len(self.user_nodes)} users, {len(self.item_nodes)} items and {len(list(self.get_rating_edges()))} ratings)"
        return message

    def get_item_nodes(self) -> Set[ItemNode]:
        return self.item_nodes

    def get_user_nodes(self) -> Set[UserNode]:
        return self.user_nodes

    def get_rating_edges(self) -> Tuple[UserNode, ItemNode]:
        for user, items in self.rating_edges.items():
            for item in items:
                yield (user, item)

    def get_user_property_edges(self) -> Tuple[UserNode, PropertyNode]:
        for node, edge in self.edges():
            if isinstance(node, UserNode) and isinstance(edge, PropertyNode):
                yield (node, edge)
            elif isinstance(node, PropertyNode) and isinstance(edge, UserNode):
                yield (edge, node)

    def get_item_property_edges(self) -> Tuple[ItemNode, PropertyNode]:
        for node, edge in self.edges():
            if isinstance(node, ItemNode) and isinstance(edge, PropertyNode):
                yield (node, edge)
            elif isinstance(node, PropertyNode) and isinstance(edge, ItemNode):
                yield (edge, node)

    def get_ratings_with_labels(self):
        ratings = defaultdict(list)
        for u, v in list(self.get_rating_edges()):
            data = self.get_edge_data(u, v)
            ratings[u].append((v, data["rating"]))

        return ratings

    def get_all_triples(self, return_type='str'):

        # ratings triples
        ratings_triples = self.get_ratings_triples(return_type=return_type)

        # user property triples
        user_property_triples = self.get_user_property_triples(return_type=return_type)

        # item property triples
        item_property_triples = self.get_item_property_triples(return_type=return_type)

        return pd.concat([ratings_triples, user_property_triples, item_property_triples])

    def get_ratings_triples(self, return_type='str'):
        triples_return = {"head": [], "relation": [], "tail": []}

        ratings = self.get_ratings_with_labels()
        desc = "Generating ratings triples"
        n_total = len(ratings.keys())
        for user, ratings in tqdm(ratings.items(), total=n_total, desc=desc):
            ratings.sort(key=lambda x: x[1], reverse=True)
            for rating in ratings:
                if return_type == "str":
                    triples_return["head"].append(user.__str__()) 
                else:
                    triples_return["head"].append(user)
                triples_return["relation"].append(f"rating{rating[1]}")
                if return_type == "str":
                    triples_return["tail"].append(rating[0].__str__())
                else:
                    triples_return["tail"].append(rating[0])

        return pd.DataFrame(triples_return)
    
    def get_user_property_triples(self, return_type='str'):
        triples_return = {"head": [], "relation": [], "tail": []}

        user_properties = self.get_user_property_edges()
        desc = "Generating user properties triples"
        for user, user_property in tqdm(user_properties, desc=desc):
            if return_type == "str":
                triples_return["head"].append(user.__str__())
            else:
                triples_return["head"].append(user)
            triples_return["relation"].append(user_property.get_property_type())
            triples_return["tail"].append(user_property.get_id())

        return pd.DataFrame(triples_return)
    
    def get_item_property_triples(self, return_type='str'):
        triples_return = {"head": [], "relation": [], "tail": []}

        item_properties = self.get_item_property_edges()
        desc = "Generating item properties triples"
        for item, item_property in tqdm(item_properties, desc=desc):
            if return_type == "str":
                triples_return["head"].append(item.__str__())
            else:
                triples_return["head"].append(item)
            triples_return["relation"].append(item_property.get_property_type())
            triples_return["tail"].append(item_property.get_id())

        return pd.DataFrame(triples_return)

    def get_user_rated_items(self, user: UserNode) -> Set[ItemNode]:
        return self.rating_edges[user]

    def add_node(self, node_for_adding: Node, **attr):
        super().add_node(node_for_adding, **attr)
        if isinstance(node_for_adding, ItemNode):
            self.item_nodes.add(node_for_adding)
        elif isinstance(node_for_adding, UserNode):
            self.user_nodes.add(node_for_adding)

    def add_edge(self, u_of_edge, v_of_edge, **attr):
        super().add_edge(u_of_edge, v_of_edge, **attr)
        data = self.get_edge_data(u_of_edge, v_of_edge, default={})
        edge_type = data.get("type")

        if edge_type == "rated":
            self.rating_edges[u_of_edge].add(v_of_edge)
            self.rating_item2users[v_of_edge].add(u_of_edge)

    def remove_edge(self, u, v):
        if isinstance(u, UserNode) and isinstance(v, ItemNode):
            self.rating_edges[u].remove(v)
            self.rating_item2users[v].remove(u)

        super().remove_edge(u, v)

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

    def convert_node_labels_to_integer(self):
        N = self.number_of_nodes()
        mapping = dict(zip(self.nodes(), range(0, N)))
        G = nx.relabel_nodes(self, mapping, copy=True)
        nx.set_node_attributes(G, {v: k for k, v in mapping.items()}, "old_label")

        G.item_nodes = self.item_nodes.copy()
        G.user_nodes = self.user_nodes.copy()
        G.rating_edges = self.rating_edges.copy()
        G.rating_item2users = self.rating_item2users.copy()

        return G

    def convert_back(self):
        mapping = {node: self.nodes[node]["old_label"] for node in self.nodes()}
        G = nx.relabel_nodes(self, mapping, copy=True)
        nx.set_node_attributes(G, {v: k for k, v in mapping.items()}, "old_label")

        G.item_nodes = self.item_nodes.copy()
        G.user_nodes = self.user_nodes.copy()
        G.rating_edges = self.rating_edges.copy()
        G.rating_item2users = self.rating_item2users.copy()

        return G

    def __read_csv(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        col_names = []
        for col in df.columns:
            try:
                col_name, data_type = col.split("::")
                col_names.append(col_name)

                if data_type == "string":
                    df[col] = df[col].astype(str)
                elif data_type == "string_list":
                    df[col] = df[col].apply(lambda x: str(x).split("::"))
                elif data_type == "number":
                    df[col] = pd.to_numeric(df[col])
            except Exception as e:
                print(
                    f"Couldn't parse data type of column named {col}. Should be col_name::data_type"
                )
                print(f"Supported types are: string, string_list, number")
                exit()
        df.columns = col_names

        return df

    def _add_item_info(self, item, enrich):
        # Extracting info from .csv
        df_item = self.__read_csv(item["path"])
        extra_features = get_optional_argument(item, "extra_features", [])
        df_item = df_item[["item_id"] + extra_features]
        if enrich is not None:
            # Merging info from original dataset and enriched
            df_map = self.__read_csv(enrich["map_path"])
            df_item = pd.merge(df_item, df_map, on="item_id", how="left")
            if enrich["remove_unmatched"]:
                df_item = df_item[df_item["URI"].notna()]

            df_enriched = self._get_enrich_dataframe(**enrich)
            df_item = pd.merge(df_item, df_enriched, on="item_id", how="left")

        # Creating graph from dataframe
        desc = "Adding item info into network"
        n_items = df_item.shape[0]
        properties = list(df_item.columns)
        properties.remove("item_id")

        # Adding item nodes and properties nodes
        for _, row in tqdm(df_item.iterrows(), total=n_items, desc=desc):
            item_node = ItemNode(row["item_id"])
            self.add_node(item_node)

            for property_ in properties:
                self._add_node_property(item_node, row, property_)

    def _add_node_property(self, source: Node, row: pd.Series, property_: str):
        prop_value = row[property_]
        if not isinstance(prop_value, list) and pd.notna(prop_value):
            # Single property_
            property_node = PropertyNode(row[property_], property_)
            self.add_edge(source, property_node, type="has_property")
        elif isinstance(prop_value, list):
            # Multiples properties
            for value in row[property_]:
                property_node = PropertyNode(value, property_)
                self.add_edge(source, property_node, type="has_property")

    def _get_optional_argument(self, config, key, default):
        try:
            return config[key]
        except KeyError:
            return default

    def _get_enrich_dataframe(self, **enrich_config):
        df_enriched = self.__read_csv(enrich_config["enrich_path"])
        properties = enrich_config["properties"]
        df_enriched = df_enriched[["item_id"] + properties]

        return df_enriched

    def _add_user_info(self, user):
        df_user = self.__read_csv(user["path"])
        extra_features = get_optional_argument(user, "extra_features", [])
        df_user = df_user[["user_id"] + extra_features]

        total_users = df_user.shape[0]
        desc = "Adding user info into network"
        properties = list(df_user.columns)
        properties.remove("user_id")

        for _, row in tqdm(df_user.iterrows(), total=total_users, desc=desc):
            user_node = UserNode(row["user_id"])
            self.add_node(user_node)

            for property_ in properties:
                self._add_node_property(user_node, row, property_)

    def _add_ratings(self, ratings):
        df_ratings = self.__read_csv(ratings["path"])
        total_ratings = df_ratings.shape[0]
        desc = "Adding ratings into network"

        for _, row in tqdm(df_ratings.iterrows(), total=total_ratings, desc=desc):
            item_node = ItemNode(row["item_id"])
            user_node = UserNode(row["user_id"])

            if item_node in self and user_node in self:
                attrs = {"type": "rated", "rating": row["rating"]}
                if ratings["timestamp"]:
                    attrs["timestamp"] = row["timestamp"]

                self.add_edge(user_node, item_node, **attrs)

    def _add_social_links(self, social):
        df_social = self.__read_csv(social["path"])
        total_links = df_social.shape[0]
        desc = "Adding social links between users into network"

        for _, row in tqdm(df_social.iterrows(), total=total_links, desc=desc):
            user1_node = UserNode(row["user1"])
            user2_node = UserNode(row["user2"])

            if user1_node in self and user2_node in self:
                self.add_edge(user1_node, user2_node)
