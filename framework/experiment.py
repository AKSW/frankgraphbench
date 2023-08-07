import yaml
import json

from .dataloader.dataloader import load

def run(config_path):
    config = None
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    load(**config['experiment']['dataset'])

