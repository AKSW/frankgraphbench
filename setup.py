from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="FranKGraphBench",
    version="0.1.0",
    author="Paulo do Carmo and Alvaro Lopes",
    author_email='paulo.carmo@htwk-leipzig.de',
    url='https://github.com/AKSW/frankgraphbench/tree/main/',
    description="pip install package for frankgraphbench.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(
        where='src',
    ),
    package_dir={
        "": "src",
    },
    install_requires=[
        'gensim', 'joblib', 'networkx==3.1', 'numpy==1.24', 'pandas==2.0', 'python-dateutil', 'pytz', 'PyYAML', 'scikit-learn==1.3', 'scipy==1.10', 'six', 'smart-open',
        'threadpoolctl', 'tqdm', 'tzdata', 'pykeen', 'torch==2.1.2', 'py-cpuinfo', 'gputil', 'psutil', 'sentence-transformers', 'graph-walker', 'isodate==0.6',
        'Levenshtein==0.21', 'pyparsing==3.0', 'python-Levenshtein==0.21', 'rapidfuzz==3.0', 'rdflib==6.3', 'SPARQLWrapper==2.0', 'thefuzz==0.19', 'tzdata==2023.3',
        'beautifulsoup4', 'matplotlib==3.7', 'contourpy==1.1'
    ],
    entry_points={
        'console_scripts': [
            'framework=framework:framework',
            'data_integration=data_integration:data_integration',
            'chart_generation=chart_generation:chart_generation'
        ],
    },
    license='Apache-2.0',
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        'Programming Language :: Python :: 3',
    ],

)