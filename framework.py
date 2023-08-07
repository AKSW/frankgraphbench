import argparse
from framework.experiment import run

def main():
    parser = argparse.ArgumentParser(
        description="Script to run framework for reproducible experiment."
    )

    parser.add_argument('-c', '--config',  type=str, required=True, help='.yml config filepath to setup experiment')

    args = parser.parse_args()
    config_path = args.config
    print(f'Running experiment defined by {config_path} ...')
    run(config_path)


if __name__ == '__main__':
    main()