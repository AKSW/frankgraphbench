# Add Evaluation Metric

To add a evaluation metric follow these steps:

1. Fork the dataset, pull the latest changes and create a new branch 
***add-metric-{metric_name}***

2. In the submodule `framework/evaluator/`, implement a [`Metric`](https://github.com/AlvaroJoseLopes/Knowledge-Graph-aware-Recommender-Systems-with-DBpedia/blob/main/framework/evaluator/metric.py) subclass for your dataset. 
    * `from ..metric import Metric`
    * Your subclass must override the following methods: 
        - `__init__()` to instantiate the class.
        - `name()` that returns the metric name.
        - `eval()` that evaluates the recommendations using the metric.
    *  Your code must be placed in a new file at `framework/evaluator/metrics/`. 

3. Store the submodule path to dinamically load the subclass.
    * Go to the `framework/evaluator/metric2class.py` file. This file store the mapping between the metric name and the submodule path and class name.
    * Create a new key with the metric's name. This name will be used by the framework to identify the metric.
    * Store in this new key, the `submodule:` path, from `framework/evaluator/`, and the `class:` name.
    * For example:
        ```python
        metric2class = {
            # ...
            'MAP': { # metric name
                'submodule': 'metrics.map', # submodule path
                'class': 'MAP'              # class name    
            }
        }
        ```

4. Add the metric into the documentation
    * In the file `docs/source/getting_started/support.md` and **Evaluation Metrics** section, add the metric to the list.
    * Inform the metric name with reference link.

5. Make a Pull Request on Github with your contribution.