# Supported Datasets, Models and Others

## Datasets

Currently the supported datasets are:

| Dataset | #items matched | #items | name |
|---------|---------------|---|-----|
|[MovieLens-100k](https://grouplens.org/datasets/movielens/100k/)|1462|1681|ml-100k|
|[MovieLens-1M](https://grouplens.org/datasets/movielens/1m/)|3356|3883|ml-1m|
|[LastFM-hetrec-2011](https://grouplens.org/datasets/hetrec-2011/)|11815|17632|lastfm|
|[Douban-Movie-Short-Comments-Dataset](https://www.kaggle.com/datasets/utmhikari/doubanmovieshortcomments/data)|---|28|douban-movie|
|[Yelp-Dataset](https://www.yelp.com/dataset/download)|---|150348|yelp|
|[Amazon-Video-Games-5](https://nijianmo.github.io/amazon/index.html)|---|21106|amazon-video_games-5|

## Models

Currently the supported Recommender System models are:

### deepwalk_based
- Node embedding based model (Node2Vec) + cosine similarity. (DeepWalk equivalent model can be run by setting the parameters `p` and `q` to `1.0`)
  - References: 
    - DeepWalk: Bryan Perozzi, Rami Al-Rfou, and Steven Skiena. 2014. Deepwalk: Online learning of social representations. In Proceedings of the 20th ACM SIGKDD international conference on Knowledge discovery and data mining. 701–710.
    - node2vec: Aditya Grover and Jure Leskovec. 2016. node2vec: Scalable feature learning for networks. In Proceedings of the 22nd ACM SIGKDD international conference on Knowledge discovery and data mining. 855–864.
  - Main parameters
    - `walk_len`: random walk length that determines how many nodes will be explore in a single walk.
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
    - `random_seed`: seed for the sampling of the triples during, training, testing and validation.
    - `triples`: if the model is going to be trained using all triples or just rating typed triples, either `"all"` or `"ratings"`.
### transH
- TransH graph embedding + cosine similarity.
  - Reference: Zhen Wang, Jianwen Zhang, Jianlin Feng, and Zheng Chen. 2014. Knowledge graph embedding by translating on hyperplanes. In Proceedings of the AAAI conference on artificial intelligence, Vol. 28.
  - Main parameters
    - `embedding_dim`: the entity embedding dimension, usually between `50` and `300`.
    - `scoring_fct_norm`: the norm applied in the interaction function, usually `1` or `2`.
    - `epochs`: number of training iterations.
    - `random_seed`: seed for the sampling of the triples during, training, testing and validation.
    - `triples`: if the model is going to be trained using all triples or just rating typed triples, either `"all"` or `"ratings"`.
### transR
- TransR graph embedding + cosine similarity.
  - Reference: Yankai Lin, Zhiyuan Liu, Maosong Sun, Yang Liu, and Xuan Zhu. 2015. Learning entity and relation embeddings for knowledge graph completion. In Proceedings of the AAAI conference on artificial intelligence, Vol. 29.
  - Main parameters
    - `embedding_dim`: the entity embedding dimension, usually between `50` and `300`.
    - `relation_dim`: the relation embedding dimension, usually equal or smaller than `embedding_dim`.
    - `scoring_fct_norm`: the norm applied in the interaction function, usually `1` or `2`.
    - `epochs`: number of training iterations.
    - `random_seed`: seed for the sampling of the triples during, training, testing and validation.
    - `triples`: if the model is going to be trained using all triples or just rating typed triples, either `"all"` or `"ratings"`.
### transD
- TransD graph embedding + cosine similarity.
  - Reference: Guoliang Ji, Shizhu He, Liheng Xu, Kang Liu, and Jun Zhao. 2015. Knowledge graph embedding via dynamic mapping matrix. In Proceedings of the 53rd annual meeting of the association for computational linguistics and the 7th international joint conference on natural language processing (volume 1: Long papers). 687–696.
  - Main parameters
    - `embedding_dim`: the entity embedding dimension, usually between `50` and `300`.
    - `relation_dim`: the relation embedding dimension, usually equal or smaller than `embedding_dim`.
    - `epochs`: number of training iterations.
    - `random_seed`: seed for the sampling of the triples during, training, testing and validation.
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
    - `apply_batch_normalization`: wheter to apply batch normalization (`bool`).
    - `epochs`: number of training iterations.
    - `random_seed`: seed for the sampling of the triples during, training, testing and validation.
    - `triples`: if the model is going to be trained using all triples or just rating typed triples, either `"all"` or `"ratings"`.

### rESCAL
- RESCAL graph embedding + cosine similarity.
  - Reference: Maximilian Nickel, Volker Tresp, Hans-Peter Kriegel, et al. 2011. A three-way model for collective learning on multi-relational data. In Icml, Vol. 11. 3104482–3104584.
  - Main parameters
    - `embedding_dim`: the entity embedding dimension, usually between `50` and `300`.
    - `epochs`: number of training iterations.
    - `random_seed`: seed for the sampling of the triples during, training, testing and validation.
    - `triples`: if the model is going to be trained using all triples or just rating typed triples, either `"all"` or `"ratings"`.

### complEx
- ComplEx graph embedding + cosine similarity.
  - Reference: Théo Trouillon, Johannes Welbl, Sebastian Riedel, Éric Gaussier, and Guillaume Bouchard. 2016. Complex embeddings for simple link prediction. In International conference on machine learning. PMLR, 2071–2080.
  - Main parameters
    - `embedding_dim`: the entity embedding dimension.
    - `epochs`: number of training iterations.
    - `random_seed`: seed for the sampling of the triples during, training, testing and validation.
    - `triples`: if the model is going to be trained using all triples or just rating typed triples, either `"all"` or `"ratings"`.

### ePHEN
- EPHEN embedding propagation + start embedding model + cosine similarity.
  - Reference: Paulo do Carmo and Ricardo Marcacini. 2021. Embedding propagation over heterogeneous event networks for link prediction. In 2021 IEEE International Conference on Big Data (Big Data). 4812–4821.
  - Main parameters
    - `embedding_model`: the start embedding model name, either a hugginface sentence transformer model or a previously implemented graph embedding model.
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


## Pre-processing Methods

Those are the currently supported pre-processing methods:
* Binarize ratings.
* Filtering by k-core

## Splitting Methods

Currently the supported Splitting method are:
* Random by Ratio
* Timestamp by Ratio
* Fixed Timestamp
* K-Fold

## Evaluation Metrics

Those are the already implemented metrics:
* MAP@k
* nDCG@k

## Chart Generation

Currently the supported charts are:

| Chart |
|-------|
|[CD-Diagram](https://github.com/hfawaz/cd-diagram)|