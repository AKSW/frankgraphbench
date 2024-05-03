# Supported Datasets, Models and Others

## Datasets

Currently the supported datasets are:

| Dataset | #items matched | #items | name |
|---------|---------------|---|-----|
|[MovieLens-100k](https://grouplens.org/datasets/movielens/100k/)|1462|1681|ml-100k|
|[MovieLens-1M](https://grouplens.org/datasets/movielens/1m/)|3356|3883|ml-1m|
|[LastFM-hetrec-2011](https://grouplens.org/datasets/hetrec-2011/)|11815|17632|lastfm|
|[Douban-Movie-Short-Comments-Dataset](https://www.kaggle.com/datasets/utmhikari/doubanmovieshortcomments/data)|28|---|douban-movie|
|[Yelp-Dataset](https://www.yelp.com/dataset/download)|150348|---|yelp|
|[Amazon-Video-Games-5](https://nijianmo.github.io/amazon/index.html)|21106|---|amazon-video_games-5|

## Models

Currently the supported Recommender System models are:

- **deepwalk_based**: Node embedding based model (Node2Vec) + cosine similarity.
  - Reference: X
  - Main parameters
    - `walk_len`: random walk length.
    - `n_walks`: number of random walks for each node.
    - `p`: likelihood of returning to the previous node, promoting more exploration of local structures.
    - `q`: likelihood of moving away from the previous node, promoting more exploration of different parts of the graph.
    - `embedding_size`: embedding size.
    - `window_size`: Word2Vec window size.

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