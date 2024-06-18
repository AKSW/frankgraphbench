import argparse
from framework.experiment import run

__version__ = "0.1.0"
__author__ = "Paulo do Carmo and Alvaro Lopes"

def framework():
    parser = argparse.ArgumentParser(
        description="Script to run framework for reproducible experiment."
    )

    parser.add_argument('-c', '--config',  type=str, required=True, help='.yml config filepath to setup experiment')

    args = parser.parse_args()
    config_path = args.config
    print(f'Running experiment...')
    run(config_path)