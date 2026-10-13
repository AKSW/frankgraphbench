import platform
import sys

from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

# TensorFlow is installed differently depending on the platform.
#
# * Apple Silicon (macOS, arm64): the regular `tensorflow` wheel does not ship a
#   usable arm64 build, so we install `tensorflow-macos` (the Apple-Silicon build
#   of the tensorflow runtime) together with `tensorflow-metal` (the Metal
#   accelerator). The plain `tensorflow` package is *not* installed so it cannot
#   shadow `tensorflow-macos`.
# * Every other platform (Linux, Windows, x86 macOS): install the regular
#   `tensorflow` package as normal.
#
# This is evaluated at install time, so `pip install frankgraphbench` picks the
# correct TensorFlow variant automatically for the machine it runs on.
is_apple_silicon = sys.platform == "darwin" and platform.machine() == "arm64"

if is_apple_silicon:
    tensorflow_requires = [
        "tensorflow-macos",
        "tensorflow-metal",
    ]
else:
    tensorflow_requires = [
        "tensorflow",
    ]

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
        'gensim', 'joblib', 'networkx', 'numpy', 'pandas', 'python-dateutil', 'pytz', 'PyYAML', 'scikit-learn', 'scipy', 'six', 'smart-open',
        'threadpoolctl', 'tqdm', 'tzdata', 'pykeen', 'torch==2.2', 'py-cpuinfo', 'gputil', 'psutil', 'tf-keras', 'sentence-transformers', 'isodate',
        'Levenshtein', 'pyparsing', 'python-Levenshtein', 'rapidfuzz', 'rdflib', 'SPARQLWrapper', 'thefuzz', 'tzdata',
        'beautifulsoup4', 'matplotlib', 'contourpy', 'SPARQLWrapper', 'multiprocess', 'ollama', 'polars', 'pyarrow',
        *tensorflow_requires,
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