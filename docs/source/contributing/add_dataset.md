# Add Dataset

To support a new Dataset into the Data Integration step follow these steps:

1. Fork the repository, pull the latest changes and create a new branch ***add-dataset-{dataset_name}***

2. Create a bash script to download the raw data and store it into a new folder with the name of the dataset. 
   * Place it into the [`datasets/`](https://github.com/AlvaroJoseLopes/Knowledge-Graph-aware-Recommender-Systems-with-DBpedia/tree/main/datasets) folder.

3. Implement a [`Dataset`](https://github.com/AlvaroJoseLopes/Knowledge-Graph-aware-Recommender-Systems-with-DBpedia/blob/main/data_integration/dataset.py) subclass for your dataset. 
    * `from ..dataset import Dataset`
    * Your subclass must override the following methods: 
        - `__init__()` to instantiate the class.
        - `load_item_data()` for converting the item data into a `pd.DataFrame()`.
        - `load_user_data()` for converting the user data into a `pd.DataFrame()`.
        - `load_rating_data()` for converting the rating data into a `pd.DataFrame()`.
        - `load_social_data()` for converting the social link data into a `pd.DataFrame()`, if supported.
        - `entity_linking()` for matching each item with a DBpedia resource.
        - `enrich()` for enriching each item with DBpedia's properties.
    *  Your code must be placed in a new file at `data_integration/datasets/`. 

4. Store the submodule path to dinamically load the subclass.
    * Go to the `data_integration/dataset2class.py` file. This file store the mapping between the dataset name and the submodule path and class name.
    * Create a new key with the dataset's name. This dataset name will be used to identify the dataset when using the `data_integration.py` script.
    * Store in this new key, the `submodule:` path, from `data_integration/`, and the `class:` name.
    * For example:
        ```python
        dataset2class = {
            # ....
            'ml-100k': {    # Dataset name
                'submodule': 'datasets.movielens',  # submodule path
                'class': 'MovieLens100k'            # Class name
            }
        }
        ```

5. Add the dataset into the documentation
    * In the file `docs/source/getting_started/support.md` and **Datasets** section, add the dataset to the table.
    * Inform the dataset name with reference link, number of matched items and total number of items of the dataset.

6. Make a Pull Request on Github.