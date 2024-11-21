#!/bin/sh
# install Douban movie dataset (https://www.kaggle.com/datasets/utmhikari/doubanmovieshortcomments)
# curl <YOUR WGET LINK FROM KAGGLE> --output douban.zip
unzip douban.zip -d douban-movie/
rm douban.zip