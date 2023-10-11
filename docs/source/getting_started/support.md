# Supported Datasets, Models and Others

## Datasets

Currently the supported datasets are:

| Dataset | #items matched | #items | name |
|---------|---------------|---|-----|
|[MovieLens-100k](https://grouplens.org/datasets/movielens/100k/)|1462|1681|ml-100k|
|[MovieLens-1M](https://grouplens.org/datasets/movielens/1m/)|3356|3883|ml-1m|
|[LastFM-hetrec-2011](https://grouplens.org/datasets/hetrec-2011/)|11815|17632|lastfm| 

## Models

Currently the supported Recommender System models are:

* **deepwalk_based**: Node embedding based model (Node2Vec) + cosine similarity

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