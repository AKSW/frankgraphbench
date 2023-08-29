# Knowledge-Graph-aware-Recommender-Systems-with-DBpedia
Repository containing Data Integration between DBpedia and some standard Recommender Systems datasets and framework for reproducible experiments. For more info, check [project proposal](https://github.com/AlvaroJoseLopes/GSoC-2023) and project progress with weekly (as possible) [updates](https://github.com/AlvaroJoseLopes/Knowledge-Graph-aware-Recommender-Systems-with-DBpedia/wiki). 

# Data Integration Usage
Install the require packages using python [virtualenv](https://docs.python.org/3/library/venv.html), using:

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
python3 data_integration.py [-h] -d DATASET -i INPUT_PATH -o OUTPUT_PATH [-ci] [-cu] [-cr] [-map]
```

Arguments:
- **-h:** Shows the help message.
- **-d:** Name of a supported dataset. Will be the same name of the folder created by the bash script provided for the dataset. For now, check `data_integration/dataset2class.py` to see the supported ones.
- **-i:** Input path where the full dataset is placed.
- **-o:** Output path where the integrated dataset will be placed.
- **-ci:** Use this flag if you want to convert item data.
- **-cu:** Use this flag if you want to convert user data.
- **-cr:** Use this flag if you want to convert rating data.
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
    item: # infos related to item dataset (mandatory, at least item_id)
      path: datasets/ml-100k/processed/item.csv 
      extra_features: [movie_year, movie_title] # features(columns) beside item_id to be used
    user: # mandatory (at least user_id)
      path: datasets/ml-100k/processed/user.csv 
      extra_features: [gender, occupation] # features beside user_id
    ratings: # mandatory (at least [user_id, item_id, rating])
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
    - method: filter_by_rating  
      parameters:
        min: 3  #inclusive
        max: 11 #inclusive
    - method: binarize
      parameters: 
        threshold: 4
    - method: filter_kcore
      parameters:
        core: 5
        iterations: 3
        target: user # user or rating

  split:
    seed: 42
    test:
      method: random_by_ratio 
      level: global 
      p: 0.2
    validation:
      method: random_by_ratio 
      level: global 
      p: 0.2

  models:
    - name: deepwalk_based
      config:
      parameters:
        walk_len: 10
        n_walks: 5
        embedding_size: 64
        epochs: 2
```

See the [config_files/](/config_files/) directory for more examples.

Notes: WIP