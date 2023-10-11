# Introduction
This project was designed to support further contributions, whether adding new supported datasets or new baseline models and bug fixing. 

## Basic Workflow

1. Fork repository
   * Go to the [repository](https://github.com/AlvaroJoseLopes/Knowledge-Graph-aware-Recommender-Systems-with-DBpedia) and click on the "fork" button
   * Clone the forked repository to your local computer:
        ```bash
        git clone git@github.com:your-username/repo_name.git
        ```
    * Navigate to the folder and add the upstream repository:
        ```bash
        cd repo_name
        git remote add upstream git@github.com:AlvaroJoseLopes/Knowledge-Graph-aware-Recommender-Systems-with-DBpedia.git
        ```
    * **Note**: Now you have two remote repositories. `upstream` which refers to the original repository and `origin` which refers to your fork.

2. Set up environment:
   * Before contributing make sure to initialize the virtual environment using [virtualenv](https://docs.python.org/3/library/venv.html)
        ```shell
        python3 -m venv venv/
        source venv/bin/activate
        pip3 install -r requirements_framework.txt # or requirements_data_integration.txt
        ```
   * **Notes**: 
     - If you are contributing to Data Integration step, make sure to use `requirements_data_integration.txt` and add any additional dependency.
     - If you are contributing to the Framework, make sure to use `requirements_framework.txt` and add any additional dependency.

3. Develop your contribution:
    * Pull the latest changes from upstream:
        ```bash
        git checkout main
        git pull upstream main
        ```
    * Create a branch for the contribution you want to work on. Make sure to use a meaningful name, such as add-dataset-LibraryThing.
        ```bash
        git checkout -b add-dataset-LibraryThing main
        ```
    * Commit your changes locally

4. Make sure to test your contribution

5. Submit your contribution
    * Push your changes to your forked repository:
        ```bash
        git push origin add-dataset-LibraryThing
        ```
    * Go to Github and make a Pull Request. 

## More details

Checkout in more details on how to contribute to each part of the project:
* [Adding new Dataset](./add_dataset.md) (Data Integration)
* [Adding new Recommender System model](./add_recommender.md) (Framework:Recommender)
* [Adding new Evaluation Metric](./add_metric.md) (Framework:Evaluator)
* [Adding new Splitting Metric](./add_splitting.md) (Framework:Dataloader)
* [Adding new Preprocessing method](./add_preprocess.md) (Framework:Dataloader)
* [Bug fixing](./bug_fixing.md)