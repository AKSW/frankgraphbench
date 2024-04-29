#!/bin/sh
# install Yelp challenge dataset (https://www.kaggle.com/datasets/yelp-dataset/yelp-dataset?resource=download)
# curl <YOUR WGET LINK FROM KAGGLE> --output yelp.zip
unzip yelp.zip -d yelp/
rm yelp.zip