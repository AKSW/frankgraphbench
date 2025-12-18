from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="FranKGraphBench",
    version="0.1.2",
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
        'gensim', 'joblib', 'networkx', 'numpy<2', 'pandas', 'python-dateutil', 'pytz', 'PyYAML', 'scikit-learn', 'scipy', 'six', 'smart-open',
        'threadpoolctl', 'tqdm', 'tzdata', 'pykeen', 'torch==2.2', 'py-cpuinfo', 'gputil', 'psutil', 'tf-keras', 'sentence-transformers', 'graph-walker', 'isodate',
        'Levenshtein', 'pyparsing', 'python-Levenshtein', 'rapidfuzz', 'rdflib', 'SPARQLWrapper', 'thefuzz', 'tzdata',
        'beautifulsoup4', 'matplotlib', 'contourpy', 'SPARQLWrapper', 'multiprocess', 'tensorflow'
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