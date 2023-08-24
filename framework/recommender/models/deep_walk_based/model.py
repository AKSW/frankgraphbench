from ...recommender import Recommender
from ...utils.walker import BiasedRandomWalker 

from gensim.models.word2vec import Word2Vec
import walker
import numpy as np
import networkx as nx

class DeepWalkBased(Recommender):
    def __init__(
            self, 
            config : dict, 
            walk_len : int, 
            n_walks : int, 
            p : float = 1.0,
            q : float = 1.0,
            embedding_size : int = 64,
            workers : int = 4,
            window_size : int = 3,
            epochs: int = 1,
            learning_rate : float = 0.05,
            min_count : int = 1,
            seed : int = 42 
        ):
        super().__init__(config)
        self.walk_len = walk_len
        self.n_walks = n_walks
        self.embedding_size = embedding_size
        self.p, self.q = p, q
        self.workers = workers
        self.window_size = window_size
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.min_count = min_count
        self.seed = seed

    def train(self, G_train, ratings_train, labels_train):
        self.fit(G_train)
    
    def fit(self, graph):

        self._convert_node_labels_to_integer(graph)
        self.walks = walker.random_walks(
            graph, n_walks=self.n_walks, walk_len=self.walk_len
        )
        print(f'Random walk shape: {self.walks.shape}')
        self.walks = self.walks.tolist()

        model = Word2Vec(
            self.walks,
            sg=1,
            hs=1,
            alpha=self.learning_rate,
            epochs=self.epochs,
            vector_size=self.embedding_size,
            window=self.window_size,
            min_count=self.min_count,
            workers=self.workers,
            seed=self.seed
        )

        self._embedding = {}
        for node in list(graph.nodes())[:10]:
            # self._embedding[node] = model.wv[str(node)]
            self._embedding[graph.nodes[node]['old_label']] = model.wv[node]

        # convert back?
        
        print(self._embedding)
        self._convert_back(graph)
        print(list(graph.nodes())[:5])

    def get_embedding(self):
        return np.array(self._embedding)
    
    def _convert_node_labels_to_integer(self, G):
        N = G.number_of_nodes()
        mapping = dict(zip(G.nodes(), range(0, N)))
        nx.relabel_nodes(G, mapping, copy=False)
        nx.set_node_attributes(G, {v: k for k, v in mapping.items()}, 'old_label')

    def _convert_back(self, G):
        mapping = {node: G.nodes[node]['old_label'] for node in G.nodes()}
        nx.relabel_nodes(G, mapping, copy=False)
        nx.set_node_attributes(G, {v: k for k, v in mapping.items()}, 'old_label')


           
    
