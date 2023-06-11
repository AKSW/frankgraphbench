# Knowledge-Graph-aware-Recommender-Systems-with-DBpedia
Repository containing Data Integration between DBpedia and some standard Recommender Systems datasets and framework for reproducible experiments.

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
python3 data_integration.py -d 'ml-100k' -i 'datasets/ml-100k' -o 'datasets/ml-100k/processed' -ci -cu -cr -map
```

Check [Makefile](Makefile) for more examples.

## Supported datasets

| Dataset | #items matched | #items |
|---------|---------------|---|
|[MovieLens-100k](https://grouplens.org/datasets/movielens/100k/)|1462|1681|
|[MovieLens-1M](https://grouplens.org/datasets/movielens/1m/)|3356|3883|
|[LastFM-hetrec-2011](https://grouplens.org/datasets/hetrec-2011/)|11815|17632| 


