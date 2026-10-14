# Introduction

This project is an outcome of [Google Summer of Code 2023](https://summerofcode.withgoogle.com/programs/2023/projects/3NTZTLYb)
project at DBpedia named FranKGraphBench: Reproducible Benchmarking for Knowledge Graph-based Recommendation. The Framework was accepted at the Resource Track from the 35th ACM International Conference on Information and Knowledge Management in Rome, Italy from the 7th to 11th November 2026.

This project has three main components:

- **Data Integration**: for loading standard datasets that will be evaluated in the Recommendation task. It also allows enriching them with Knowledge Graphs and related datasets through a map and enrichment interface.
- **Framework**: for running reproducible experiments on enriched and non-enriched datasets through a `.yml` configuration file.
- **Chart Generation**: for visualizing the generated results with full control from the user using a Command-Line Interface.

As part of the Data Integration module we fixed and used the DBpedia 2016-10 core version, accessible through the endpoint [endpoint](https://dbfk25.aksw.org/sparql/) and with .ttl files downloadable [here](https://dbfk25.aksw.org/).


![project pipeline](../imgs/framework.svg)
