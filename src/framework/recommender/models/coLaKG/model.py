from __future__ import annotations

import json
import os
import re
import time

import numpy as np
import torch
from ollama import Client
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

from ....dataloader.graph.graph import Graph
from ....dataloader.graph.node import ItemNode, PropertyNode, UserNode
from ....reporter.report import get_host_info
from ....utils import get_optional_argument
from ...recommender import Recommender
from .CoLaKG import CoLaKG_model
from .colakg_utils import BPRLoss
from .dataloader import Loader
from .Procedure import BPR_train_original, Test
from .walker import parallel_random_walks


def _batch(iterable, batch_size):
    """Yield successive slices of ``iterable`` of at most ``batch_size`` items."""
    for i in range(0, len(iterable), batch_size):
        yield iterable[i:i + batch_size]


class CoLaKG(Recommender):
    # Random-walk variant used to build the user prompts. The parallel walker
    # derives a per-node RNG from ``(walk_seed, node_index)``, which is not
    # byte-identical to the legacy sequential single-RNG stream, so it is part of
    # the cache key to stop an old-seed cache being served under new walk content.
    _WALK_VARIANT = "parallel-cow-v1"

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
            walk_seed: int = 42,
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
        self.walk_seed = walk_seed
        self.validate_frac = validate_frac
        self.validate_seed = validate_seed
        self.epochs = epochs
        self.device = torch.device(
             device if device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.item_llm_limit = item_llm_limit
        self.user_llm_limit = user_llm_limit
        # Optional flag (read from the model `config:` block, like save_weights)
        # that forces the LLM response cache to be regenerated. A cache is also
        # regenerated automatically when its stored system prompt no longer
        # matches the current one, regardless of this flag.
        self.reset_cache = get_optional_argument(config, 'reset_cache', False)
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

        client = Client(host=self.model_host)

        # Get (or reuse cached) LLM responses for items and users, then embed
        # them. The cache lives under datasets/<dataset>/colakg-cache/ and is
        # keyed by the LLM model and target type; see _get_or_cache_responses.
        llm_responses_items_dict = self._get_or_cache_responses(
             client, "item",
             self.__build_input_item, self.item_system_prompt, self.item_llm_limit,
        )
        llm_responses_users_dict = self._get_or_cache_responses(
             client, "user",
             self.__build_input_user, self.user_system_prompt, self.user_llm_limit,
        )

        semantic_embs_items_dict = self.__get_emb_ollama(client, llm_responses_items_dict, "item", count_limit=self.item_llm_limit)
        semantic_embs_users_dict = self.__get_emb_ollama(client, llm_responses_users_dict, "user", count_limit=self.user_llm_limit)

        print("pre-training finished...")

        return semantic_embs_items_dict, semantic_embs_users_dict

    def _dataset_name(self) -> str:
        return self.G_train.name if hasattr(self.G_train, "name") else "unknown"

    @staticmethod
    def _sanitize_name(name: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "_", str(name)).strip("_") or "unknown"

    def _cache_dir(self) -> str:
        # <repo_root>/datasets/<dataset>/colakg-cache
        # repo root = 4 levels up from this file
        #   model.py -> coLaKG -> models -> recommender -> framework -> src -> root
        src_root = os.path.abspath(
             os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, os.pardir)
        )
        dataset_root = os.path.join(src_root, "datasets", self._dataset_name())
        return os.path.join(dataset_root, "colakg-cache")

    def _cache_path(self, target_type: str) -> str:
        # The user prompts depend on the random-walk seed, so it is part of the
        # user cache filename -- changing the seed yields a different path, so an
        # old-seed cache is naturally not reused. Item prompts don't use the walk,
        # so the item filename stays seed-independent (one item file per model).
        filename = f"{self._sanitize_name(self.model_name)}-{target_type}"
        if target_type == "user":
            filename += f"-walkseed-{self.walk_seed}"
        return os.path.join(self._cache_dir(), f"{filename}.json")

    def _load_cache(self, target_type: str, system_prompt: str):
        """Load a cached response file, validating compatibility.

        Returns (cache_dict, compatible) where cache_dict is the parsed JSON
        (or {} if the file is missing) and compatible is False when the cache
        must be regenerated -- either because it is absent, its stored system
        prompt no longer matches, it was generated for a different dataset, or it
        was produced by a different random-walk variant.
        """
        path = self._cache_path(target_type)
        if not os.path.exists(path):
            return {}, False
        try:
            with open(path, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: could not read cache '{path}': {e}. Regenerating.")
            return {}, False

        if cache.get("system_prompt") != system_prompt:
            print(f"Prompt mismatch for '{target_type}': regenerating cache (ignoring reset_cache).")
            return cache, False
        if cache.get("dataset") != self._dataset_name():
            print(f"Dataset mismatch for '{target_type}': regenerating cache.")
            return cache, False
        # The user cache filename already encodes the walk seed, so a seed change
        # naturally points at a different (absent) file. This is a defensive
        # guard for any pre-existing cache that predates the seed in the name.
        if target_type == "user" and cache.get("walk_seed") != self.walk_seed:
            print("Walk-seed mismatch for 'user': regenerating cache.")
            return cache, False
        # The user prompts are derived from random walks. A different walker
        # variant produces different walks for the same seed, so the stored
        # variant must match to avoid serving stale prompts. Caches written
        # before this guard carried no ``walk_variant`` and are regenerated.
        if target_type == "user" and cache.get("walk_variant") != self._WALK_VARIANT:
            print(f"Walk-variant mismatch for 'user': regenerating cache.")
            return cache, False
        return cache, True

    def _write_cache(self, target_type: str, system_prompt: str, responses: dict,
                     count_limit, cache_time_seconds, computer):
        path = self._cache_path(target_type)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        payload = {
             "dataset": self._dataset_name(),
             "target_type": target_type,
             "llm_model": self.model_name,
             "emb_model": self.emb_model_name,
             "system_prompt": system_prompt,
             "walk_seed": self.walk_seed,
             "walk_variant": self._WALK_VARIANT,
             "computer": computer,
             "cache_time_seconds": cache_time_seconds,
             "count_limit": count_limit,
             "responses": responses,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"Saved LLM response cache for '{target_type}' to {path}")

    def _build_ordered_nodes(self, build_fn, system_prompt, target_type: str):
        """Build the per-node LLM prompts and return (ordered_node_ids, messages_by_id).

        Iterating by ``id`` reproduces the same LLM call order (and hence the
        same ``count_limit`` truncation) as the original implementation.
        """
        messages_by_id = {}
        for node, messages in build_fn(system_prompt).items():
            messages_by_id[id(node)] = {"node": node, "messages": messages}
        ordered_node_ids = sorted(messages_by_id, key=lambda nid: messages_by_id[nid]["node"].get_id())
        return ordered_node_ids, messages_by_id

    def _get_or_cache_responses(self, client: Client, target_type: str,
                                build_fn, system_prompt: str, count_limit: int | None):
        """Return LLM responses for ``target_type``, reusing the cache when
        possible and (re)generating + persisting it otherwise.

        The cache is *forced* to regenerate when ``reset_cache`` is set or when
        the stored cache is not compatible (missing file, or its stored system
        prompt / dataset no longer match -- a prompt mismatch always wins over
        ``reset_cache``). Otherwise cached responses are reused and only the
        missing nodes are sent to the LLM, then the merged set is written back.
        Generation time is measured separately and stored with the computer info.
        """
        cache, compatible = self._load_cache(target_type, system_prompt)
        force_regenerate = self.reset_cache or not compatible
        # When forcing a regenerate we ignore any cached responses entirely.
        cached_responses = {} if force_regenerate else cache.get("responses", {})

        ordered_node_ids, messages_by_id = self._build_ordered_nodes(
             build_fn, system_prompt, target_type,
        )

        # Walk nodes in the canonical (id) order -- the same order the LLM loop
        # uses -- and serve each from the cache where possible, otherwise mark
        # it for generation. Stopping at count_limit reproduces the original
        # truncation semantics.
        selected = []
        for nid in ordered_node_ids:
            node = messages_by_id[nid]["node"]
            node_id = str(node.get_id())
            if count_limit is not None and len(selected) >= count_limit:
                break
            if cached_responses.get(node_id) is not None:
                selected.append((node, "cache", cached_responses[node_id]))
            else:
                selected.append((node, "gen", None))

        result = {node: text for node, source, text in selected if source == "cache"}
        nodes_to_generate = [node for node, source, _ in selected if source == "gen"]

        cache_time_seconds = 0.0
        generated = {}
        if nodes_to_generate:
            generate_messages = {messages_by_id[id(n)]["node"]: messages_by_id[id(n)]["messages"]
                                 for n in nodes_to_generate}
            start = time.time()
            generated = self.__get_ollama(client, generate_messages, target_type, count_limit=None)
            cache_time_seconds = time.time() - start

        if generated:
            for node, text in generated.items():
                result[node] = text
            # Merge new responses into the previously cached ones (force mode
            # starts from an empty dict, so this writes a fresh cache).
            merged = dict(cached_responses)
            merged.update({str(n.get_id()): t for n, t in result.items()})
            self._write_cache(
                 target_type, system_prompt, merged,
                 count_limit, cache_time_seconds, get_host_info(),
            )
            print(f"Generated LLM responses for '{target_type}' "
                  f"({len(generated)} generated, {len(result)} total, "
                  f"{cache_time_seconds:.2f}s).")
        else:
            print(f"Reusing LLM response cache for '{target_type}' "
                  f"({len(result)} responses).")

        return result

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
        walks = parallel_random_walks(
             self.G_train,
             n_walks=1,
             walk_len=self.walk_len,
             start_nodes=users,
             seed=self.walk_seed,
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
