from __future__ import annotations

import time

import numpy as np
import torch
from ollama import Client
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

from ....dataloader.graph.graph import Graph
from ....dataloader.graph.node import ItemNode, PropertyNode, UserNode
from ...recommender import Recommender
from .CoLaKG import CoLaKG_model
from .colakg_utils import BPRLoss
from .dataloader import Loader
from .Procedure import BPR_train_original, Test
from .walker import random_walks


def _batch(iterable, batch_size):
    """Yield successive slices of ``iterable`` of at most ``batch_size`` items."""
    for i in range(0, len(iterable), batch_size):
        yield iterable[i:i + batch_size]


class CoLaKG(Recommender):
    def __init__(
            self,
            config: dict,
            item_name: str,
            model_host: str,
            model_name: str,
            emb_model_name: str,
            item_system_prompt: str,
            user_system_prompt: str,
            walk_len: int = 10,
            validate_frac: float = 0.01,
            validate_seed: int = 42,
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
            A_split: bool = False,
            bigdata: int = 0,
            neighbor_k: int = 10,
            dropout_i: float = 0.6,
            dropout_u: float = 0.6,
            dropout_n: float = 0.6,
            seed: int = 2020,
            epochs: int = 1000,
            semantic_hid_dim: int = 32,
            item_llm_limit: int | None = None,
            user_llm_limit: int | None = None,
            device: str = "cpu",
        ):
        super().__init__(config)
        self.item_name = item_name
        self.model_host = model_host
        self.model_name = model_name
        self.emb_model_name = emb_model_name
        self.item_system_prompt = item_system_prompt
        self.user_system_prompt = user_system_prompt
        self.walk_len = walk_len
        self.validate_frac = validate_frac
        self.validate_seed = validate_seed
        self.epochs = epochs
        self.device = torch.device(
             device if device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.item_llm_limit = item_llm_limit
        self.user_llm_limit = user_llm_limit
        self.config = {
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
             "semantic_hid_dim": semantic_hid_dim,
        }

    def name(self):
        text = "CoLaKG"
        text += f";model={self.model_name};emb_model={self.emb_model_name};walk_len={self.walk_len}"
        return text

    def train(self, G_train: Graph, ratings_train):
        self.ratings_train = ratings_train
         # Keep the original-node graph for prompt building but register the
         # canonical 0-based int id-map that get_ratings_triples("int") requires.
        self.G_train = G_train.convert_node_labels_to_integer(int_id_map=True)
        self._int_id_map = self.G_train._int_id_map

        self.item_property_dict = {item: [] for item in self.G_train.get_item_nodes()}
        for item, property in self.G_train.get_item_property_edges():
            self.item_property_dict[item].append(property)

        self.semantic_embs_items_dict, self.semantic_embs_users_dict = self._pre_train()

         # The semantic embedding dimension (drives the semantic maps in the model).
        self.semantic_dim = None
        for emb in self.semantic_embs_items_dict.values():
            self.semantic_dim = len(emb)
            break
        if self.semantic_dim is None:
            for emb in self.semantic_embs_users_dict.values():
                self.semantic_dim = len(emb)
                break
        if self.semantic_dim is None:
            raise RuntimeError("No semantic embeddings were produced; check model_host and the LLM/embedding limits.")

        self.fit()

    def fit(self):
        import random
        random.seed(self.config["seed"])
        np.random.seed(self.config["seed"])

        n_items = self._int_id_map["n_items"]
        n_users = self._int_id_map["n_users"]
        item_id = self._int_id_map["items"]
        user_id = self._int_id_map["users"]

         # Align the LLM-generated embeddings to the model's 0-based int id space.
         # Pad any node that missed an embedding (LLM/embed limit) with zeros so
         # that node index i <-> semantic row i, matching get_ratings_triples("int").
        item_rows = [np.zeros(self.semantic_dim, dtype=np.float32) for _ in range(n_items)]
        for item, emb in self.semantic_embs_items_dict.items():
            item_rows[item_id[item]] = np.asarray(emb, dtype=np.float32)

        user_rows = [np.zeros(self.semantic_dim, dtype=np.float32) for _ in range(n_users)]
        for user, emb in self.semantic_embs_users_dict.items():
            user_rows[user_id[user]] = np.asarray(emb, dtype=np.float32)

        item_semantic_emb = torch.tensor(np.asarray(item_rows)).to(self.device)
        user_semantic_emb = torch.tensor(np.asarray(user_rows)).to(self.device)

         # Global information: k-nearest semantic neighbors over item embeddings.
        cosine_sim_matrix = cosine_similarity(item_semantic_emb.detach().cpu().numpy())
        sorted_indices = np.argsort(-cosine_sim_matrix, axis=1)
        sorted_indices = sorted_indices[:, 1:self.config["neighbor_k"] + 1]   # does not include itself
        sorted_indices = torch.tensor(sorted_indices).long().to(self.device)

        ratings_triples = self.G_train.get_ratings_triples(return_type="int")
        self.dataset = Loader(self.config, ratings_triples, self.validate_frac, self.validate_seed)

        self.model = CoLaKG_model(
             self.config,
             self.dataset,
             sorted_indices,
             item_semantic_emb,
             user_semantic_emb,
             self.device,
         )
        bpr = BPRLoss(self.model, self.config)

        for epoch in range(self.epochs):
            start = time.time()

            if epoch % 5 == 0:
                print("[TEST]")
                test_results = Test(
                     self.dataset, self.model, epoch,
                     topks=(1, 10, 100),
                     u_batch_size=self.config["test_u_batch_size"],
                )
                print(f"TEST RESULTS at EPOCH[{epoch+1}/{self.epochs}]: {test_results}")

            output_information = BPR_train_original(
                 self.dataset, self.model, bpr, epoch,
                 batch_size=self.config["bpr_batch_size"],
            )

            end = time.time()
            epoch_time = end - start

            print(f"Epoch [{epoch+1}/{self.epochs}] {output_information} - completed in {epoch_time:.2f} seconds")

    def get_recommendations(self, k: int = 5) -> dict[UserNode, list[ItemNode]]:
         # Reverse maps: canonical int id -> original Node object.
        item_id = self._int_id_map["items"]
        user_id = self._int_id_map["users"]
        int_to_user = {int_id: u for u, int_id in user_id.items()}
        int_to_item = {int_id: i for i, int_id in item_id.items()}

         # Items each user has seen in training, keyed by int id for fast masking.
        seen_by_user = {}
        for user in self.G_train.get_user_nodes():
            seen_by_user[user_id[user]] = {item_id[i] for i in self.G_train.get_user_rated_items(user)}

        all_int_users = list(user_id.values())
        u_batch_size = self.config["test_u_batch_size"]
        recommendations = {int_to_user[u]: [] for u in all_int_users}

        self.model.eval()
        with torch.no_grad():
            for batch in _batch(all_int_users, u_batch_size):
                batch_int = torch.tensor(batch, dtype=torch.long).to(self.device)
                rating = self.model.getUsersRating(batch_int)    # (batch, n_items)
                rating = rating.detach().cpu().numpy()

                for idx, u_int in enumerate(batch):
                    scores = rating[idx].copy()
                       # Mask items the user has already seen in training.
                    for item_int in seen_by_user.get(u_int, ()):
                        scores[item_int] = -1e10
                       # Top-k by score, then back to original ItemNode objects.
                    topk = np.argsort(-scores)[:k]
                    recommendations[int_to_user[u_int]] = [int_to_item[i] for i in topk]

        return recommendations

    def get_user_recommendation(self, user: UserNode, k: int = 5) -> list[ItemNode]:
        recs = self.get_recommendations(k=k)
        return recs.get(user, [])

    def _pre_train(self):
        print("building input...")

        messages_items_dict = self.__build_input_item(self.item_system_prompt)
        messages_users_dict = self.__build_input_user(self.user_system_prompt)

        client = Client(host=self.model_host)
        llm_responses_items_dict = self.__get_ollama(client, messages_items_dict, "item", count_limit=self.item_llm_limit)
        llm_responses_users_dict = self.__get_ollama(client, messages_users_dict, "user", count_limit=self.user_llm_limit)

        semantic_embs_items_dict = self.__get_emb_ollama(client, llm_responses_items_dict, "item", count_limit=self.item_llm_limit)
        semantic_embs_users_dict = self.__get_emb_ollama(client, llm_responses_users_dict, "user", count_limit=self.user_llm_limit)

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
         # G_train was converted with int_id_map=True, so its nodes are the
         # original Node objects and carry no "old_label". Run one random walk
         # per user node on the graph itself to build a user-centered context.
        users = list(self.G_train.get_user_nodes())
        walks = random_walks(
             self.G_train,
             n_walks=1,
             walk_len=self.walk_len,
             start_nodes=users,
        )

          # Map each walk back to its starting user node so that the LLM/embed
          # calls are keyed by the same Node objects as the item prompts (the
          # int id is only used inside the prompt text for readability).
        user_walks = {}
        for walk in walks:
            start_user = walk[0]
              # The walk may repeat the start node; keep the rest as context.
            context = [n for n in walk[1:] if n is not start_user]
            user_walks[start_user] = context

        messages_dict = {}
        for user_node, context in user_walks.items():
            user_int = self._int_id_map["users"][user_node]
            user_content = f"user {user_int} is related, according to a random walk of length {self.walk_len}: "
            if not context:
               user_content += " no neighborhood was found."
            for node in context:
               if isinstance(node, PropertyNode):
                   user_content += f"to the property {node.get_property_type()} defined as {node.get_id()}; "
               elif isinstance(node, ItemNode):
                   if node in self.item_property_dict:
                       types_list = [prop.get_property_type() for prop in self.item_property_dict[node]]
                       if self.item_name in types_list:
                           idx = types_list.index(self.item_name)
                           user_content += f"to the item {node.get_id()}, named {self.item_property_dict[node][idx].get_id()}; "
                       else:
                           user_content += f"to the item {node.get_id()}; "
                   else:
                       user_content += f"to the item {node.get_id()}; "
               else:
                    # Another user in the walk; reference it by its canonical int id.
                   user_content += f"to user {self._int_id_map['users'][node]}; "

            messages_dict[user_node] = [
                 {"role": "system", "content": system_prompt},
                 {"role": "user", "content": user_content}
             ]

        return messages_dict

    def __get_ollama(self, client: Client, messages_dict: dict, target_type: str, count_limit: int | None = None):
        llm_responses_dict = {}
        for count, node in tqdm(enumerate(messages_dict), total=len(messages_dict), desc=f"requesting llm model {self.model_name} with host {self.model_host} for '{target_type}' semantic description..."):
            response = client.chat(model=self.model_name, messages=messages_dict[node], think=None)
            llm_responses_dict[node] = response["message"]["content"]

            if count_limit is not None and count >= count_limit:
                break

        return llm_responses_dict

    def __get_emb_ollama(self, client: Client, llm_responses_dict: dict, target_type: str, count_limit: int | None = None):
        semantic_embs_dict = {}
        for count, node in tqdm(enumerate(llm_responses_dict), total=len(llm_responses_dict), desc=f"generating embedding for '{target_type}' with model {self.emb_model_name}..."):
            response = client.embed(model=self.emb_model_name, input=llm_responses_dict[node])
            try:
                semantic_embs_dict[node] = response["embeddings"][0]
            except IndexError as e:
                print(f"error: {e}")
                print(response)

            if count_limit is not None and count >= count_limit:
                break

        return semantic_embs_dict
