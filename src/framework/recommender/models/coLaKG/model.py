import torch
import walker

import numpy as np
import scipy.sparse as sp

from ollama import Client
from tqdm import tqdm
from typing import Optional
from sklearn.metrics.pairwise import cosine_similarity

from .CoLaKG import CoLaKG_model
from ...recommender import Recommender
from ....dataloader.graph.node import PropertyNode, ItemNode

class CoLaKG(Recommender):
    def __init__(
            self,
            config: dict,
            item_name: str,
            model_host: str,
            model_name: str,
            emb_model_name: str,
            walk_len: int = 10,
            bpr_batch_size: int = 2048,
            latent_dim_rec: int = 64,
            lightGCN_n_layers: int = 3,
            use_drop_edge: int = 1,
            keep_prob: float = 0.8,
            A_n_fold: int = 10,
            test_u_batch_size: int = 100,
            multicore: int = 0,
            lr: float = 0.001,
            decay: float = 1e-4,
            pretrain: int = 0,
            A_split: int = 100,
            bigdata: int = 0,
            neighbor_k: int = 10,
            dropout_i: float = 0.6,
            dropout_u: float = 0.6,
            dropout_n: float = 0.6,
            seed: int = 2020,
            epochs: int = 1000,
        ):
        super().__init__(config)
        self.item_name = item_name
        self.model_host = model_host
        self.model_name = model_name
        self.emb_model_name = emb_model_name
        self.walk_len = walk_len
        self.config_dict = {
            "neighbor_k": neighbor_k,
            "dropout_i": dropout_i,
            "dropout_u": dropout_u,
            "dropout_n": dropout_n,
            "bpr_batch_size": bpr_batch_size,
            "latent_dim_rec": latent_dim_rec,
            "lightGCN_n_layers": lightGCN_n_layers,
            "use_drop_edge": use_drop_edge,
            "keep_prob": keep_prob,
            "A_n_fold": A_n_fold,
            "test_u_batch_size": test_u_batch_size,
            "multicore": multicore,
            "lr": lr,
            "decay": decay,
            "pretrain": pretrain,
            "A_split": A_split,
            "bigdata": bigdata,
            "seed": seed,
            "epochs": epochs
        }

    def name(self):
        text = "CoLaKG"
        text += f";model={self.model_name};emb_model={self.emb_model_name};walk_len={self.walk_len}"
        return text
    
    def train(self, G_train, ratings_train):
        self.ratings_train = ratings_train
        self.G_train = G_train
        
        self.item_property_dict = {item: [] for item in self.G_train.get_item_nodes()}
        for item, property in self.G_train.get_item_property_edges():
            self.item_property_dict[item].append(property)
        
        self.semantic_embs_items_dict, self.semantic_embs_users_dict = self._pre_train()

        self.fit()

    def fit(self):
        cosine_sim_matrix = cosine_similarity(list(self.semantic_embs_items_dict.values()))
        sorted_indices = np.argsort(-cosine_sim_matrix, axis=1)
        sorted_indices = sorted_indices[:, 1:self.config['neighbor_k']+1] # does not include itself
        sorted_indices = torch.tensor(sorted_indices).long()

        self.model = CoLaKG_model(self.config_dict)

    def _pre_train(self):
        print("building input...")

        system_prompt = {
            "item": ("Assume you are an expert in recommendation. "
                    "You will be given some information about an item. "
                    "Based on this information and your world knowledge, "
                    "please analyze and summarize the characteristics of this item, "
                    "and analyze what kind of users would like this item. "
                    "Your response should be a coherent paragraph with no more than 200 words."
            ),
            "user": ("Assume you are an expert in recommendation. "
                    "You will be given some information about a user. "
                    "Based on this information and your world knowledge, "
                    "please analyze and summarize the characteristics of this user, "
                    "and analyze what kind of items this user would like. "
                    "Your response should be a coherent paragraph with no more than 200 words."
            ),
        }

        messages_items_dict = self.__build_input_item(system_prompt["item"])
        messages_users_dict = self.__build_input_user(system_prompt["user"])
        
        client = Client(host=self.model_host)
        llm_responses_items_dict = self.__get_ollama(client, messages_items_dict, "item")
        llm_responses_users_dict = self.__get_ollama(client, messages_users_dict, "user")

        semantic_embs_items_dict = self.__get_emb_ollama(client, llm_responses_items_dict, "item")
        semantic_embs_users_dict = self.__get_emb_ollama(client, llm_responses_users_dict, "user")

        print("pre-training finished...")

        return semantic_embs_items_dict, semantic_embs_users_dict
    
    def _get_sparse_graph(self):
        pass

        
    def __build_input_item(self, system_prompt):
        messages_dict = {}
        for item, property_list in self.item_property_dict.items():
            types_list = [prop.get_property_type() for prop in property_list]
            if self.item_name in types_list:
                idx = types_list.index(self.item_name)
                user_content = f"{item} named {property_list[idx].get_id()} is first degree related to the property nodes: "
            else:
                user_content = f"{item} is first degree related to the property nodes: "
            for prop in property_list:
                user_content += f"called {prop.get_property_type()} and defined by {prop.get_id()}; "
            
            messages_dict[item] = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ]

        return messages_dict

    def __build_input_user(self, system_prompt):
        graph = self.G_train.convert_node_labels_to_integer()
        users = graph.get_user_nodes()
        users_int = {graph.nodes[node]["old_label"]: node for node in graph.nodes() if graph.nodes[node]["old_label"] in users}
        # creates one random walk for each item where first from the list is the item_node id
        walks = walker.random_walks(graph, n_walks=1, walk_len=self.walk_len, start_nodes=[users_int[user] for user in users])
        input_dict = {}
        for walk in walks:
            input_dict[graph.nodes[int(walk[0])]["old_label"]] = [graph.nodes[int(w)]["old_label"] for w in walk[1:]]
        
        messages_dict = {}
        for user, walk in input_dict.items():
            user_content = f"{user} is related, according a random walk of length {self.walk_len}: "
            for node in walk:
                if isinstance(node, PropertyNode):
                    user_content += f"to the property {node.get_property_type()} defined as {node.get_id()}; "
                elif isinstance(node, ItemNode):
                    types_list = [prop.get_property_type() for prop in self.item_property_dict[node]]
                    if self.item_name in types_list:
                        idx = types_list.index(self.item_name)
                        user_content += f"to the item {node.get_id()}, named {self.item_property_dict[node][idx].get_id()}; "
                    else:
                        user_content += f"to the item {node.get_id()}; "
                else:   
                    user_content += f"to the user {node.get_id()}; "
            
            messages_dict[user] = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ]
        
        return messages_dict
    
    def __get_ollama(self, client: Client, messages_dict: dict, target_type: str, count_limit: Optional[int] = None):
        count = 0
        llm_responses_dict = {}
        for node in tqdm(messages_dict, total=len(messages_dict), desc=f"requesting llm model {self.model_name} with host {self.model_host} for '{target_type}' semantic description..."):
            response = client.chat(model=self.model_name, messages=messages_dict[node])
            llm_responses_dict[node] = response["message"]["content"]
            
            count += 1
            if count_limit is not None and count >= count_limit:
                break
        
        return llm_responses_dict
    
    def __get_emb_ollama(self, client: Client, llm_responses_dict: dict, target_type: str, count_limit: Optional[int] = None):
        count = 0
        semantic_embs_dict = {}
        for node in tqdm(llm_responses_dict, total=len(llm_responses_dict), desc=f"generating embedding for '{target_type}' with model {self.emb_model_name}..."):
            response = client.embed(model=self.emb_model_name, input=llm_responses_dict[node])
            semantic_embs_dict[node] = response["embeddings"][0]
            
            count += 1
            if count_limit is not None and count >= count_limit:
                break
        
        return semantic_embs_dict
