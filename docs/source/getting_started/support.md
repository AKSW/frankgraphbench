# Supported Datasets, Models and Others

## Datasets

Currently the supported datasets are:

| Dataset | #items matched | #items | name |
|---------|---------------|---|-----|
|[MovieLens-100k](https://grouplens.org/datasets/movielens/100k/)|1411|1681|ml-100k|
|[MovieLens-1M](https://grouplens.org/datasets/movielens/1m/)|3253|3883|ml-1m|
|[LastFM-hetrec-2011](https://grouplens.org/datasets/hetrec-2011/)|8628|17632|lastfm|
|[Douban-Movie-Short-Comments-Dataset](https://www.kaggle.com/datasets/utmhikari/doubanmovieshortcomments/data)|24|28|douban-movie|
|[MIND-small](https://msnews.github.io/)|30409|51282|mind-small|
|[Yelp-Dataset](https://www.yelp.com/dataset/download)|---|150348|yelp|
|[Amazon-Video-Games-5](https://nijianmo.github.io/amazon/index.html)|---|21106|amazon-video_games-5|

Dataset enrichment is done through a fixed DBpedia endpoint available at a [Virtuoso endpoint](https://dbfk25.aksw.org/sparql), with raw files download [available](https://dbfk25.aksw.org).

## Models

Currently the supported Recommender System models are:

### deepwalk_based
- Node embedding based model (Node2Vec) + cosine similarity. (DeepWalk equivalent model can be run by setting the parameters `p` and `q` to `1.0`)
  - References:
    - DeepWalk: Bryan Perozzi, Rami Al-Rfou, and Steven Skiena. 2014. Deepwalk: Online learning of social representations. In Proceedings of the 20th ACM SIGKDD international conference on Knowledge discovery and data mining. 701–710.
    - node2vec: Aditya Grover and Jure Leskovec. 2016. node2vec: Scalable feature learning for networks. In Proceedings of the 22nd ACM SIGKDD international conference on Knowledge discovery and data mining. 855–864.
  - Main parameters
    - `walk_len`: random walk length that determines how many nodes will be explored in a single walk.
    - `n_walks`: number of random walks for each node.
    - `p`: likelihood of returning to the previous node, promoting more exploration of local structures.
    - `q`: likelihood of moving away from the previous node, promoting more exploration of different parts of the graph.
    - `embedding_size`: embedding size, usually between 64 and 128.
    - `window_size`: word2vec window size, where it determines how many of the "words" within the walk length will impact the skipgram model calculation. Usually is a smaller value than the walk length.

### transE
- TransE graph embedding + cosine similarity.
  - Reference: Antoine Bordes, Nicolas Usunier, Alberto Garcia-Duran, Jason Weston, and Oksana Yakhnenko. 2013. Translating embeddings for modeling multi-relational data. Advances in neural information processing systems 26 (2013).
  - Main parameters
    - `embedding_dim`: the entity embedding dimension, usually between `50` and `300`.
    - `scoring_fct_norm`: the norm applied in the interaction function, usually `1` or `2`.
    - `epochs`: number of training iterations.
    - `seed`: seed for the sampling of the triples during training, testing and validation.
    - `triples`: if the model is going to be trained using all triples or just rating typed triples, either `"all"` or `"ratings"`.

### transH
- TransH graph embedding + cosine similarity.
  - Reference: Zhen Wang, Jianwen Zhang, Jianlin Feng, and Zheng Chen. 2014. Knowledge graph embedding by translating on hyperplanes. In Proceedings of the AAAI conference on artificial intelligence, Vol. 28.
  - Main parameters
    - `embedding_dim`: the entity embedding dimension, usually between `50` and `300`.
    - `scoring_fct_norm`: the norm applied in the interaction function, usually `1` or `2`.
    - `epochs`: number of training iterations.
    - `seed`: seed for the sampling of the triples during training, testing and validation.
    - `triples`: if the model is going to be trained using all triples or just rating typed triples, either `"all"` or `"ratings"`.

### transR
- TransR graph embedding + cosine similarity.
  - Reference: Yankai Lin, Zhiyuan Liu, Maosong Sun, Yang Liu, and Xuan Zhu. 2015. Learning entity and relation embeddings for knowledge graph completion. In Proceedings of the AAAI conference on artificial intelligence, Vol. 29.
  - Main parameters
    - `embedding_dim`: the entity embedding dimension, usually between `50` and `300`.
    - `relation_dim`: the relation embedding dimension, usually equal or smaller than `embedding_dim`.
    - `scoring_fct_norm`: the norm applied in the interaction function, usually `1` or `2`.
    - `epochs`: number of training iterations.
    - `seed`: seed for the sampling of the triples during training, testing and validation.
    - `triples`: if the model is going to be trained using all triples or just rating typed triples, either `"all"` or `"ratings"`.

### transD
- TransD graph embedding + cosine similarity.
  - Reference: Guoliang Ji, Shizhu He, Liheng Xu, Kang Liu, and Jun Zhao. 2015. Knowledge graph embedding via dynamic mapping matrix. In Proceedings of the 53rd annual meeting of the association for computational linguistics and the 7th international joint conference on natural language processing (volume 1: Long papers). 687–696.
  - Main parameters
    - `embedding_dim`: the entity embedding dimension, usually between `50` and `300`.
    - `relation_dim`: the relation embedding dimension, usually equal or smaller than `embedding_dim`.
    - `epochs`: number of training iterations.
    - `seed`: seed for the sampling of the triples during training, testing and validation.
    - `triples`: if the model is going to be trained using all triples or just rating typed triples, either `"all"` or `"ratings"`.

### tuckER
- TuckER graph embedding + cosine similarity.
  - Reference: Ivana Balažević, Carl Allen, and Timothy M Hospedales. 2019. Tucker: Tensor factorization for knowledge graph completion. arXiv preprint arXiv:1901.09590 (2019).
  - Main parameters
    - `embedding_dim`: the entity embedding dimension.
    - `relation_dim`: the relation embedding dimension, usually equal or smaller than `embedding_dim`.
    - `dropout_0`: the first dropout, `cf.formula`.
    - `dropout_1`: the second dropout, `cf.formula`.
    - `dropout_2`: the third dropout, `cf.formula`.
    - `apply_batch_normalization`: whether to apply batch normalization (`bool`).
    - `epochs`: number of training iterations.
    - `seed`: seed for the sampling of the triples during training, testing and validation.
    - `triples`: if the model is going to be trained using all triples or just rating typed triples, either `"all"` or `"ratings"`.

### rESCAL
- RESCAL graph embedding + cosine similarity.
  - Reference: Maximilian Nickel, Volker Tresp, Hans-Peter Kriegel, et al. 2011. A three-way model for collective learning on multi-relational data. In Icml, Vol. 11. 3104482–3104584.
  - Main parameters
    - `embedding_dim`: the entity embedding dimension, usually between `50` and `300`.
    - `epochs`: number of training iterations.
    - `seed`: seed for the sampling of the triples during training, testing and validation.
    - `triples`: if the model is going to be trained using all triples or just rating typed triples, either `"all"` or `"ratings"`.

### distMult
- DistMult graph embedding + cosine similarity.
  - Reference: Bishan Yang, Scott Wen-tau Yih, Xiaodong He, Jianfeng Gao, and Li Deng. 2015. Embedding Entities and Relations for Learning and Inference in Knowledge Bases. In Int. Conference on Learning Representations. ICLR, San Diego, CA, USA, 1–12.
  - Main parameters
    - `embedding_dim`: the entity embedding dimension.
    - `epochs`: number of training iterations.
    - `seed`: seed for the sampling of the triples during training, testing and validation.
    - `triples`: if the model is going to be trained using all triples or just rating typed triples, either `"all"` or `"ratings"`.

### complEx
- ComplEx graph embedding + cosine similarity.
  - Reference: Théo Trouillon, Johannes Welbl, Sebastian Riedel, Éric Gaussier, and Guillaume Bouchard. 2016. Complex embeddings for simple link prediction. In International conference on machine learning. PMLR, 2071–2080.
  - Main parameters
    - `embedding_dim`: the entity embedding dimension.
    - `epochs`: number of training iterations.
    - `seed`: seed for the sampling of the triples during training, testing and validation.
    - `triples`: if the model is going to be trained using all triples or just rating typed triples, either `"all"` or `"ratings"`.

### rotatE
- RotatE graph embedding + cosine similarity.
  - Reference: Zhiqing Sun, Zhi-Hong Deng, Jian-Yun Nie, and Jian Tang. 2019. RotatE: Knowledge Graph Embedding by Relational Rotation in Complex Space. In Int. Conference on Learning Representations. Openreview, Louisiana, United States, 1–18.
  - Main parameters
    - `embedding_dim`: the entity embedding dimension.
    - `epochs`: number of training iterations.
    - `seed`: seed for the sampling of the triples during training, testing and validation.
    - `triples`: if the model is going to be trained using all triples or just rating typed triples, either `"all"` or `"ratings"`.

### ePHEN
- EPHEN embedding propagation + start embedding model + cosine similarity.
  - Reference: Paulo do Carmo and Ricardo Marcacini. 2021. Embedding propagation over heterogeneous event networks for link prediction. In 2021 IEEE International Conference on Big Data (Big Data). 4812–4821.
  - Main parameters
    - `embedding_model`: the start embedding model name, either a Hugging Face sentence transformer model or a previously implemented graph embedding model.
    - `embedding_model_kwargs`: arguments for the starting embedding model.
    - `embed_with`: either the `column_name` for the item property that contains text data, or `"graph"` when using a previously implemented graph embedding model.
    - `iterations`: the number of iterations for the regularization propagation.
    - `mi`: the mi factor number that dictates how much of the start embedding will affect the final embedding, values fluctuate between `0` and `1`.

### entity2rec
- Entity2Rec recommendation model based on Node2Vec.
  - Reference: Palumbo, Enrico, Giuseppe Rizzo, and Raphaël Troncy. 2017. Entity2rec: Learning user-item relatedness from knowledge graphs for top-n item recommendation. Proceedings of the eleventh ACM conference on recommender systems. 32-36.
  - Main parameters
    - `embedding_model`: the embedding model name of a previously implemented graph embedding model.
    - `embedding_model_kwargs`: arguments for the embedding model.
    - `collab_only`: using only collaboration filtering properties' embeddings for the recommendations.
    - `content_only`: using only item content properties' embeddings for the recommendations.
    - `social_only`: using only user social interaction properties' embeddings for the recommendations.
    - `workers`: the number of threads to be used in creating candidates for recommendations. `-1` automatically inputs the number of cores as the amount of workers. number of physical cores is recommended in case the computer needs to be usable for other tasks.
    - `frac_negative_candidates`: calculates a fraction from the amount of unrated items for a user to be used in the train data. Values between `0` and `1` with `0.1` recommended.
    - `seed`: seed for fixing the sampling of negative and positive examples for training.
    - `relevance`: the necessary relevance of an evaluation from a user to be counted as a recommendation.

### bPRMF
- BPR: Bayesian Personalized Ranking from Implicit Feedback.
  - Reference for implementation: Xiang Wang, Xiangnan He, Yixin Cao, Meng Liu and Tat-Seng Chua. 2019. KGAT: Knowledge Graph Attention Network for Recommendation. KDD '19: Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining. 950-958. Proposed in: Steffen Rendle, Christoph Freudenthaler, Zeno Gantner, and Lars Schmidt-Thieme. 2009. BPR: Bayesian personalized ranking from implicit feedback. Proceedings of the Twenty-Fifth Conference on Uncertainty in Artificial Intelligence (UAI '09). 452–461.
  - Main parameters
    - `embed_size`: the embedding vector size.
    - `epoch`: the amount of epochs to be used during the training of the graph neural network.
    - `validate_factor`: the amount of epochs where a validation for possible early stopping is triggered.
    - `validate_frac`: the fraction amount of the training triples to be used for validation.
    - `random_seed`: the seed for separating the validation set.
    - `test_flag`: the type of testing to be executed during validation.
    - `ks`: the evaluation type for validation.

### cKE
- CKE: Collaborative Knowledge Base Embedding for Recommender Systems.
  - Reference for implementation: Xiang Wang, Xiangnan He, Yixin Cao, Meng Liu and Tat-Seng Chua. 2019. KGAT: Knowledge Graph Attention Network for Recommendation. KDD '19: Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining. 950-958. Proposed in: Fuzheng Zhang, Nicholas Jing Yuan, Defu Lian, Xing Xie, and Wei-Ying Ma. 2016. Collaborative Knowledge Base Embedding for Recommender Systems. KDD '16: Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining. 353–362.
  - Main parameters
    - `embed_size`: the embedding vector size.
    - `kge_size`: vector size of the knowledge graph embedding.
    - `epoch`: the amount of epochs to be used during the training of the graph neural network.
    - `validate_factor`: the amount of epochs where a validation for possible early stopping is triggered.
    - `validate_frac`: the fraction amount of the training triples to be used for validation.
    - `random_seed`: the seed for separating the validation set.
    - `test_flag`: the type of testing to be executed during validation.
    - `ks`: the evaluation type for validation.


### cFKG
- CFKG: Collaborative Filtering Knowledge Graph for Recommendation.
  - Reference for implementation: Xiang Wang, Xiangnan He, Yixin Cao, Meng Liu and Tat-Seng Chua. 2019. KGAT: Knowledge Graph Attention Network for Recommendation. KDD '19: Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining. 950-958. Proposed in: Qingyao Ai, Vahid Azizi, Xu Chen, and Yongfeng Zhang. 2018. Learning Heterogeneous Knowledge Base Embeddings for Explainable Recommendation. arXiv:1805.03352.
  - Main parameters
    - `embed_size`: the embedding vector size.
    - `kge_size`: vector size of the knowledge graph embedding.
    - `epoch`: the amount of epochs to be used during the training of the graph neural network.
    - `validate_factor`: the amount of epochs where a validation for possible early stopping is triggered.
    - `validate_frac`: the fraction amount of the training triples to be used for validation.
    - `random_seed`: the seed for separating the validation set.
    - `test_flag`: the type of testing to be executed during validation.
    - `ks`: the evaluation type for validation.

### kGAT
- KGAT: Knowledge Graph Attention Network for Recommendation.
  - Reference: Xiang Wang, Xiangnan He, Yixin Cao, Meng Liu and Tat-Seng Chua. 2019. KGAT: Knowledge Graph Attention Network for Recommendation. KDD '19: Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining. 950-958.
  - Main parameters
    - `embed_size`: the embedding vector size.
    - `kge_size`: vector size of the knowledge graph embedding.
    - `layer_size`: list with the embedding size of each GNN layer.
    - `batch_size_kg`: batch size used for the knowledge graph (phase II) part.
    - `node_dropout`: per-layer node dropout rate.
    - `mess_dropout`: per-layer message dropout rate.
    - `use_att`: when `True`, the attentive laplacian matrix A is re-estimated every epoch.
    - `use_kge`: when `True`, the knowledge graph embedding (TransE) part is trained.
    - `adj_type`: type of adjacency (`si`, `bi`, ...); `adj_uni_type`: how adjacency variants are combined (`sum`, ...).
    - `alg_type`: GNN aggregation variant (`bi`, `gcn`, `graphsage`, ...).
    - `device`: execution device, `auto` (CUDA -> Metal/MPS -> CPU), `cpu`, `cuda`, or `mps`.
    - `epoch`: the amount of epochs to be used during the training of the graph neural network.
    - `validate_factor`: the amount of epochs where a validation for possible early stopping is triggered.
    - `validate_frac`: the fraction amount of the training triples to be used for validation.
    - `random_seed`: the seed for separating the validation set.
    - `test_flag`: the type of testing to be executed during validation.
    - `ks`: the evaluation type for validation.
  - Attentive matrix A (Oct 2026):
    - KGAT re-estimates the attentive adjacency A at every epoch from the current
      embeddings (`update_attentive_A`) and feeds the updated A back into the GNN
      for the next forward pass. This is the intended KGAT behaviour and is what
      allows the attention over the knowledge-graph edges to evolve as training
      progresses.
    - The original TensorFlow port captured the GNN's sparse adjacency *once* at
      graph-construction time, so the per-epoch re-estimation of A was computed but
      never re-plugged into the already-built GNN computation graph; the GNN
      effectively kept operating on the *initial* adjacency. That mismatch is a
      likely explanation for the lower-than-expected KGAT scores observed in the
      previous version.
    - The PyTorch implementation fixes this: `update_attentive_A` rebuilds the
      sparse tensor consumed by the GNN (`_A_sparse`) at the end of every call, so
      each epoch's message passing runs on the freshly re-estimated attentive
      adjacency. This applies to `use_att=True` and to the `gcn`/`graphsage`
      aggregation variants, which read the same adjacency.


## Pre-processing Methods

Those are the currently supported pre-processing methods:
* Binarize ratings.
* Filtering by k-core

## Splitting Methods

Currently the supported Splitting methods are:
* Random by Ratio
* Timestamp by Ratio
* Fixed Timestamp
* K-Fold

## Evaluation Metrics

Those are the already implemented metrics:
* MAP@k
* nDCG@k
* Precision@k
* Recall@k
* F-score@k

## Chart Generation

Currently the supported charts are:

| Chart |
|-------|
|[CD-Diagram](https://github.com/hfawaz/cd-diagram)|