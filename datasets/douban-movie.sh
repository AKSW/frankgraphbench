#!/bin/sh
# install Yelp challenge dataset (https://www.kaggle.com/datasets/yelp-dataset/yelp-dataset?resource=download)
# curl <YOUR WGET LINK FROM KAGGLE> --output douban.zip
unzip douban.zip -d douban-movie/
rm douban.zip