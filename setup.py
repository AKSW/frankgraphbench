from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

# Single source of truth: the dependency set is declared once, in requirements.txt
# (shipped in the sdist via MANIFEST.in), so install_requires stays in sync
# automatically and future upgrades edit only one file.
with open("requirements.txt", "r") as fh:
    install_requires = [
        line.strip()
        for line in fh
        if line.strip() and not line.strip().startswith("#")
    ]

setup(
    name="FranKGraphBench",
    version="0.2.1",
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
    # install_requires is read from requirements.txt above (single source of truth;
    # kept in sync automatically and shipped in the sdist via MANIFEST.in).
    install_requires=install_requires,
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