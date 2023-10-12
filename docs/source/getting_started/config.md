# Setting up configuration file

The directive `experiment` configures the experimetn pipeline that includes:

*  `dataset` configuration
*  `preprocess` methods
*  `split` method
*  `models` to be evaluated
*  `evaluation` configuration
*  `report` to summarize experiment results

Example:
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
    - name: deepwalk_based
      config:
        save_weights: True
      parameters:
        walk_len: 10
        p: 0.8
        q: 0.6
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
The next session goes through all details of each directive.

## dataset

In this section, we can define the dataset name and provide details about items, users, ratings and enriching data.

```yaml
experiment:
  dataset: 
    name: dataset_name
    item:
      path: /path/to/item.csv 
      extra_features: [feat1_name, feat2_name, ...] 
    user: 
      path: path/to/user.csv 
      extra_features: [feat1_name, feat2_name, ...] 
    ratings: 
      path: path/to/rating.csv 
      timestamp: True|False
    enrich:
      map_path: path/to/map.csv
      enrich_path: path/to/enriched.csv
      remove_unmatched: True|False
      properties: 
        # list of enriching properties 
        - type: property1_name
          grouped: True|False
          sep: separator
        - type: property1_name
          grouped: True|False
          sep: seprator
```

Let's break down the main directives for the dataset:

- `item`: specifies the item info to be added to the network. (mandatory)
  - `path`: filepath of the standardized  **item.csv**. (mandatory)
  - `extra_features`: For default, the only column to be added is the `item_id`. With a list of column names the user can specify additional features to be added as property node. (optional)
- `user`: specifies the user info. (mandatory)
  - `path`: filepath of the standardized  **user.csv**. (mandatory)
  - `extra_features`: For default, the only column to be added is the `item_id`. With a list of column names the user can specify additional features to be added as property node. (optional)
- `ratings`: specifies the ratings info. (mandatory)
  - `path`: filepath of the standardized  `ratings.csv`. (mandatory)
  - `timestamp`: boolean that indicates if the column `timestamp` is present.
- `enrich`: specifies the enriched info. (mandatory)
  - `map_path`: filepath of the standardized  `map.csv`. (mandatory)
  - `enrich_path`: filepath of the standardized  `user.csv`. (mandatory)
  - `remove_unmatched`: boolean to specify if nodes unmatched with DBpedia should be removed. (mandatory)
  - `properties`: list of properties to enrich the dataset (mandatory)
    - `type`: column name (type) of the property (mandatory)
    - `grouped`: boolean that indicates if the property was grouped and concatenated into a single string.  Used for multiples property values of the same property type for a given resource. (mandatory)
    - `sep`: separator used to concatenate a list of property values. (optional)


## preprocess

In the .yaml file, the directive **preprocess** is used to define the list of pre-processing methods to be performed during the experiment pipeline. The pre-processing step can be configured as:

```yaml
experiment:
  # ...
  preprocess:
    - method: method1_name  
      parameters:
        parameter_1: 3  
        parameter_2: val 
    - method: method2_name
      parameters: 
        parameter_1: 4
```

Where,
- `preprocess`: specifies a list of pre-processing methods. (optional)
  - `method`: method name (mandatory)
  - `parameters`: method parameters in the format `parameter_name: parameter_value`

The current supported pre-processing methods can be found in [support documentation](./support.md).


### binarize parameters

In the *.yaml* file, the method name is `binarize` and the only parameter is a `threshold` number. Example:

```yaml
experiment:
  preprocess:
    - method: binarize
      parameters: 
        threshold: 4
```

### filter_kcore parameters

In the *.yaml* file, the method name is `filter_kcore`, and the parameters are `k`, the number of `iterations` and the `target` type of node (user or item). Example:

```yaml
experiment:
  # ...
  preprocess:
    - method: filter_kcore
      parameters:
        k: 20
        iterations: 3
        target: user # user or rating
```

## split

In the .yaml file, the directive **split** is used to define the split method. For example:

```yaml
experiment:
  # ...
  split:
    seed: 42
    test:
      method: method1_name 
      parameter1_name: 0.2
      parameter2_name: value
    validation:
      method: method2_name 
      parameter1_name: value_2
      parameter2_name: 100
```

Where,
- `split`: specifies the splitting method used. (mandatory)
  - `seed`: random seed value for reproducibility 
  - `test`: directive for the test split
  - `validation`: directive for the validation split 
  - `method`: splitting method name (mandatory)
    - Parameters as a dictionary where the key is the splitting method parameter name and the value is the corresponding value of this parameter. Example: `parameter1: value1`

The current supported splitting methods can be found in [support documentation](./support.md).

### random_by_ratio parameters

In the *.yaml* file, the method name is `random_by_ratio`, and the parameters are:
- `p`: test set proportion (mandatory)
- `level`: **global** or **user** level (mandatory).

Example:

```yaml
experiment:
  # ...
  split:
    seed: 42
    test:
      method: random_by_ratio 
      level: global # or user
      p: 0.2
    validation:
      method: random_by_ratio 
      level: global # or user
      p: 0.2
```

### timestamp_by_ratio parameters

In the *.yaml* file, the method name is `timestamp_by_ratio`, and the parameters are the same as Random by Ratio. Example:

```yaml
experiment:
  # ...
  split:
    test:
      method: timestamp_by_ratio 
      level: user # or global
      p: 0.1
    validation:
      method: timestamp_by_ratio 
      level: user # or global
      p: 0.2
```

### fixed_timestamp parameters

In the *.yaml* file, the method name is `fixed_timestamp`. The only parameter is the `timestamp` number. Example:

```yaml
experiment:
  # ...
  split:
    test:
      method: fixed_timestamp 
      timestamp: 890000000
    validation:
      method: fixed_timestamp 
      timestamp: 880000000
```

### k_fold parameters

In the *.yaml* file, the method name is `k_fold`. The parameters are:
- `k`: number of folds (mandatory)
- `level`: **global** or **user** level (mandatory).

**Note:** This method does not support validation splitting.

Example:
```yaml
experiment:
  # ...
  split:
    test:
      method: k_fold
      k: 3 
      level: 'user'
```

## models

In the *.yaml* file, the **models** directive defines a list of models to be evaluated during the experiment pipeline. Example:

```yaml
experiment:
  models:
    - name: deepwalk_based
      config:
        save_weights: True
      parameters:
        parameter1: 10
        paramater2: value
    - # Other model to be evaluated...
```

Where,
- `models`: specifies a list of models to be evaluated. (mandatory)
  - `name`: model name (mandatory)
  - `config`: metadata config
    - *save_weights*: boolean that indicates if the model parameters must be saved after training.
  - `parameters`: model parameters in the format `parameter_name: parameter_value` 

The supported models and their parameters can be found at the [support](./support.md) documentation.

## evaluation

In the *.yaml* file, the **evaluation** directive defines the experiment evaluation. The evaluation metadata is given in the format `metadata1: metadata1_value`.  Example:

```yaml
experiment:
  # ...
  evaluation:
    k: 5
    relevance_threshold: 3
    metrics: [MAP, nDCG]
```

Where,
- `evaluation`: specifies the evaluation metadata (mandatory)
  - `k`: evaluates the first k recommendations (mandatory)
  - `relevance_threshold`: threshold value to consider a rating relevant.  
  - `metrics`: list of metric names to be evaluated. (mandatory)

Check out the availables evaluation metric in the [support](./support.md) documentation. 

## report 

In the *.yaml* file, the **report** directive defines the experiment summarization. 

```yaml
experiment:
  # ...
  report:
    file: 'experiment_results/ml100k_enriched/run1.csv'
```

Where,
- `report`: specifies the report metadata (mandatory)
  - `file`: ***.csv*** filename of the experiment report. (mandatory)




