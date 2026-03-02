# FranKGraphBench: Knowledge Graph Aware Recommender Systems Framework for Benchmarking
[![DOI](https://zenodo.org/badge/646290327.svg)](https://doi.org/10.5281/zenodo.14513776)

The FranKGraphBench is a framework to allow KG Aware RSs to be benchmarked in a reproducible and easy to implement manner. 
It was first created on Google Summer of Code 2023 for Data Integration between DBpedia and some standard RS datasets in a reproducible framework.

Check the [docs](https://frankgraphbench.readthedocs.io/en/latest/index.html) for more information.

* This repository was first created for Data Integration between DBpedia and some standard Recommender Systems datasets and a framework for reproducible experiments. For more info, check the [project proposal](https://github.com/AlvaroJoseLopes/GSoC-2023) and the project progress with weekly (as possible) [updates](https://github.com/AKSW/frankgraphbench/wiki).

# Data Integration

## pip

We recommend using a python 3.8 virtual environment:

```shell
pip install pybind11
pip install frankgraphbench
```

Install the full dataset using bash scripts located at `datasets/`:

```shell
cd datasets
bash ml-100k.sh # Downloaded at `datasets/ml-100k` folder
bash ml-1m.sh   # Downloaded at `datasets/ml-1m` folder
```

## Source

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
data_integration [-h] -d DATASET -i INPUT_PATH -o OUTPUT_PATH [-ci] [-cu] [-cr] [-cs] [-map] [-enrich] [-w]
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
- **-enrich:** Use this flag if you want to enrich dataset with DBpedia.
- **-w:** Choose the number of workers(threads) to be used for parallel queries.

pip example:

```shell
data_integration -d 'ml-100k' -i 'datasets/ml-100k' -o 'datasets/ml-100k/processed' \
    -ci -cu -cr -map -enrich -w 8
```

source example:
```shell
python3 src/data_integration.py -d 'ml-100k' -i 'datasets/ml-100k' -o 'datasets/ml-100k/processed' \
    -ci -cu -cr -map -enrich -w 8
```

Check [Makefile](Makefile) for more examples.

## Supported datasets

| Dataset | #items matched | #items |
|---------|---------------|---|
|[MovieLens-100k](https://grouplens.org/datasets/movielens/100k/)|1411|1681|
|[MovieLens-1M](https://grouplens.org/datasets/movielens/1m/)|3253|3883|
|[LastFM-hetrec-2011](https://grouplens.org/datasets/hetrec-2011/)|8628|17632|
|[Douban-Movie-Short-Comments-Dataset](https://www.kaggle.com/datasets/utmhikari/doubanmovieshortcomments/data)|24|28|douban-movie|
|[MIND-small](https://msnews.github.io/)|30409|51282|mind-small|
|[Yelp-Dataset](https://www.yelp.com/dataset/download)|---|150348|yelp|
|[Amazon-Video-Games-5](https://nijianmo.github.io/amazon/index.html)|---|21106|amazon-video_games-5|

Dataset enrichment, except for the MIND-small dataset, is done through a fixed DBpedia endpoint available at https://dbfk25.aksw.org/sparql, with raw files download available at https://dbfk25.aksw.org/.

# Framework for reproducible experiments

## pip

For x86 windows and linux PCs we recommend using a python 3.8 virtual environment. For Apple Silicon we recommend a python 3.11 virtual environment and using the manual install with `requirements_framework_apple.txt`, however the deep_walk_based embedding method does not work in this version:

```shell
pip install pybind11
pip install frankgraphbench
```

## source

Install the require packages using python [virtualenv](https://docs.python.org/3/library/venv.html), using:

```shell
python3 -m venv venv_framework/
source venv_framework/bin/activate
pip3 install -r requirements_framework.txt 
```

### Apple silicon

```shell
python3 -m venv venv_framework/
source venv_framework/bin/activate
pip3 install -r requirements_framework_apple.txt
```

## Usage 

pip:
```shell
framework -c 'config_files/test.yml'
```

source:
```shell
python3 src/framework.py -c 'config_files/test.yml'
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

## Supported Pre-processing Methods

Those are the currently supported pre-processing methods:
* Binarize ratings.
* Filtering by k-core

## Supported Splitting Methods

Currently the supported Splitting method are:
* Random by Ratio
* Timestamp by Ratio
* Fixed Timestamp
* K-Fold

## Supported Evaluation Metrics

Those are the already implemented metrics:
* MAP@k
* nDCG@k
* Precision@k
* Recall@k
* F-score@k

# Chart generation

Chart generation module based on: https://github.com/hfawaz/cd-diagram

## pip

We recommend using a python 3.8 virtual environment

```shell
pip install pybind11
pip install frankgraphbench
```

## source

Install the required packages using python [virtualenv](https://docs.python.org/3/library/venv.html), using:

```shell
python3 -m venv venv_chart_generation/
source venv_chart_generation/bin/activate
pip3 install -r requirements_chart_generation.txt 
```
After obtaining results from some experiments, you can use this module to generate charts for them. The module is based on the CD-Diagram, which is a chart to compare multiple methods across multiple datasets and metrics. It is based on the Critical Difference diagram, but with some modifications to allow it to be more informative and easier to read.


## Usage
pip:
```shell
chart_generation [-h] -c CHART -p PERFORMANCE_METRIC -f INPUT_FILES -i INPUT_PATH -o OUTPUT_PATH -n FILE_NAME
```

source:
```shell
python3 src/chart_generation.py [-h] -c CHART -p PERFORMANCE_METRIC -f INPUT_FILES -i INPUT_PATH -o OUTPUT_PATH -n FILE_NAME
```

Arguments:
- **-h:** Shows the help message.
- **-p:** Name of the performance metric within the file to use for chart generation.
- **-f:** List of .csv files to use for generating the chart.
- **-i:** Path where results data to generate chart is located in .csv files.
- **-o:** Path where generated charts will be placed.
- **-n:** Add a name (and file extension) to the chart that will be generated.

Examples:

pip:
```shell
chart_generation -c 'cd-diagram' -p 'MAP@5' -f "['ml-100k.csv', 'ml-1m.csv', 'lastfm.csv', 'ml-100k_enriched.csv', 'ml-1m_enriched.csv', 'lastfm_enriched.csv']" -i 'experiment_results' -o 'charts' -n 'MAP@5.pdf'
```

source:
```shell
python3 src/chart_generation.py -c 'cd-diagram' -p 'MAP@5' -f "['ml-100k.csv', 'ml-1m.csv', 'lastfm.csv', 'ml-100k_enriched.csv', 'ml-1m_enriched.csv', 'lastfm_enriched.csv']" -i 'experiment_results' -o 'charts' -n 'MAP@5.pdf'
```

## Supported charts

| Chart |
|-------|
|[CD-Diagram](https://github.com/hfawaz/cd-diagram)|
