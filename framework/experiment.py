import yaml
import json
import importlib

from .dataloader.dataloader import load, preprocess, split
from .recommender.model2class import model2class
from .evaluator.metric2class import metric2class

import networkx as nx

def _load_model_class(name):
    # relative path from root
    module_name = f'framework.recommender.models.{model2class[name]["submodule"]}'
    class_name = model2class[name]['class']
    return module_name, class_name

def _load_metric_class(name):
    # relative path from root
    module_name = f'framework.evaluator.{metric2class[name]["submodule"]}'
    class_name = metric2class[name]['class']
    return module_name, class_name

def run(config_path):
    config = None
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print(json.dumps(config, indent=4))
    experiment = config['experiment']

    G = load(**experiment['dataset'])
    preprocess(G, experiment['preprocess'])
    print(f'Final graph: {G.info()}')

    # Extracting evaluation metrics
    evaluation_config = experiment['evaluation']
    eval_metrics = []
    for metric in evaluation_config['metrics']:
        module_name, class_name = _load_metric_class(metric)
        metric_class = getattr(importlib.import_module(module_name), class_name)
        metric_instance = metric_class(evaluation_config['k'], evaluation_config['relevance_threshold'])
        eval_metrics.append(metric_instance)
    print(f'Used metrics: {eval_metrics}')
    
    # Loop over dataset (specially if its a k-fold split)
    for dataset in split(G, **experiment['split']):
        print(G.info()) 

        for model_config in experiment['models']:
            # Loading model dinamically 
            module_name, class_name = _load_model_class(model_config['name'])
            model = getattr(importlib.import_module(module_name), class_name)
            model = model(model_config['config'], **model_config['parameters'])
            
            # Training model
            G_train, ratings_train = dataset.get_train_data()
            model.train(G_train, ratings_train)

            # Getting recomendations
            # From this data I can evaluate the result for validation and test data
            x = model.get_recommendations()

            user = list(G.get_user_nodes())[0]
            print(f'Chosen user: {user}')
            print(f'Recommendations from get_recommendations {x[user]}')
            print(f'Recommendations from get_user_recommendations: {model.get_user_recommendation(user)}')

            # Evaluate metrics for this dataset




