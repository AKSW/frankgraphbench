#!/bin/sh
# install yelp challenge dataset version 4
wget https://www.kaggle.com/datasets/yelp-dataset/yelp-dataset/download?datasetVersionNumber=4 --output-file yelp-4.zip
unzip yelp-4.zip -d lastfm/
rm yelp-4.zip
