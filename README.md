# FranKGraphBench: Knowledge Graph Aware Recommender Systems Framework for Benchmarking

The FranKGraphBench is a benchmark for Recommender Systems.
It contains the major knowledge graphs and Recommender Systems to speed up the development and facilitate the benchmarking of new methods. 

Check the [docs](https://frankgraphbench.readthedocs.io/en/latest/index.html) for more information.

* This repository was first created for Data Integration between DBpedia and some standard Recommender Systems datasets and a framework for reproducible experiments. For more info, check the [project proposal](https://github.com/AlvaroJoseLopes/GSoC-2023) and the project progress with weekly (as possible) [updates](https://github.com/AKSW/frankgraphbench/wiki).

# Data Integration Usage
Install the required packages using python [virtualenv](https://docs.python.org/3/library/venv.html), using:

```shell
python3 -m venv venv_data_integration/
source venv_data_integration/bin/activate
pip3 install -r requirements_data_integration.txt 
```

Install the full dataset using bash scripts located at `datasets/`:

```shell
cd datasets
bash ml-100k.sh # Downloaded at `datasets/ml-100k` folder
bash ml-1m.sh   # Downloaded at `datasets/ml-1m` folder
```

## Usage
```shell
python3 data_integration.py [-h] -d DATASET -i INPUT_PATH -o OUTPUT_PATH [-ci] [-cu] [-cr] [-cs] [-map] [-w]
```

Arguments:
- **-h:** Shows the help message.
- **-d:** Name of a supported dataset. It will be the same name of the folder created by the bash script provided for the dataset. For now, check `data_integration/dataset2class.py` to see the supported ones.
- **-i:** Input path where the full dataset is placed.
- **-o:** Output path where the integrated dataset will be placed.
- **-ci:** Use this flag if you want to convert item data.
- **-cu:** Use this flag if you want to convert user data.
- **-cr:** Use this flag if you want to convert rating data.
- **-cs:** Use this flag if you want to convert social link data.
- **-map:** Use this flag if you want to map dataset items with DBpedia. At least the item data should be already converted.
- **-w:** Choose the number of workers(threads) to be used for parallel queries.

Usage Example:

```shell
python3 data_integration.py -d 'ml-100k' -i 'datasets/ml-100k' -o 'datasets/ml-100k/processed' \
    -ci -cu -cr -map -w 8
```

Check [Makefile](Makefile) for more examples.

## Supported datasets

| Dataset | #items matched | #items |
|---------|---------------|---|
|[MovieLens-100k](https://grouplens.org/datasets/movielens/100k/)|1462|1681|
|[MovieLens-1M](https://grouplens.org/datasets/movielens/1m/)|3356|3883|
|[LastFM-hetrec-2011](https://grouplens.org/datasets/hetrec-2011/)|11815|17632| 

# Framework for reproducible experiments usage
Install the require packages using python [virtualenv](https://docs.python.org/3/library/venv.html), using:

```shell
python3 -m venv venv_framework/
source venv_framework/bin/activate
pip3 install -r requirements_framework.txt 
```

## Usage 

```shell
python3 framework.py -c 'config_files/test.yml'
```
Arguments:
- **-c:** Experiment configuration file path.

The experiment config file should be a .yaml file like this:

```yaml
experiment:
  dataset: 
    name: ml-100k
    item:
      path: datasets/ml-100k/processed/item.csv 
      extra_features: [movie_year, movie_title] 
    user:
      path: datasets/ml-100k/processed/user.csv 
      extra_features: [gender, occupation] 
    ratings: 
      path: datasets/ml-100k/processed/rating.csv 
      timestamp: True
    enrich:
      map_path: datasets/ml-100k/processed/map.csv
      enrich_path: datasets/ml-100k/processed/enriched.csv
      remove_unmatched: False
      properties:
        - type: subject
          grouped: True
          sep: "::"
        - type: director
          grouped: True
          sep: "::"

  preprocess:
    - method: filter_kcore
      parameters:
        k: 20
        iterations: 1
        target: user

  split:
    seed: 42
    test:
      method: k_fold
      k: 2
      level: 'user'


  models:
    - name: deepwalk_based
      config:
        save_weights: True
      parameters:
        walk_len: 10
        p: 1.0
        q: 1.0
        n_walks: 50
        embedding_size: 64
        epochs: 1
  
  evaluation:
    k: 5
    relevance_threshold: 3
    metrics: [MAP, nDCG]

  report:
    file: 'experiment_results/ml100k_enriched/run1.csv'
```

See the [config_files/](/config_files/) directory for more examples.
