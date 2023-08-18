import yaml
import json

from .dataloader.dataloader import load, preprocess, split

def run(config_path):
    config = None
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print(json.dumps(config, indent=4))

    G = load(**config['experiment']['dataset'])
    preprocess(G, config['experiment']['preprocess'])
    for x in split(G, **config['experiment']['split']):
        print(x.ratings_test)    

