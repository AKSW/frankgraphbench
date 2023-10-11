# Add Recommender System Model

To support a new RS model into the Data Integration step follow these steps:

1. Fork the repository, pull the latest changes and create a new branch ***add-model-{model_name}***

2. Create a new folder for your model inside `framework/recommender/models/`.

3. In this new submodule, implement a [`Recommender`](https://github.com/AlvaroJoseLopes/Knowledge-Graph-aware-Recommender-Systems-with-DBpedia/blob/main/framework/recommender/recommender.py) subclass. 
   * `from ...recommender import Recommender`
   * Your subclass must override the following methods:
     - `__init__()` to instantiate your class that takes as argument a config and all other arguments suited for your class.
     - `name()` that returns the model name. This name will be used in the experiment report as identification.
     - `train()` that defines the model training.
     - `get_recommendations()` that returns the model recommendations for all users.
     - `get_user_recommendations()` that return the model recommendations for a given user.
   * **Note:** In the `/recommender/utils/` you can reuse some methods that are commonly used by other models. If you are implementing a method that you believe can be reused to implement other models, please consider implementing those methods into the `utils` package.

4. Store the submodule path to dinamically load the subclass.
    * Go to the `recommender/model2class.py` file. This file store the mapping between the model name and the submodule path and class name.
    * Create a new key with the model's name. This model name will be used to identify the RS model when using the framework.
    * Store in this new key, the `submodule:` path, from `framework/recommender/models`, and the `class:` name.
    * For example:
        ```python
        model2class = {
            # ...
            'deepwalk_based': { # model name
                'submodule': 'deep_walk_based.model',   # submodule path
                'class': 'DeepWalkBased'                # class name
            }
        }
        ```

5. Add the model into the documentation
    * In the file `docs/source/getting_started/support.md` and **Models** section, add the model into the list.
    * Inform the model name, a reference and model summary (main components of the architecture).

6. Make a Pull Request on Github.