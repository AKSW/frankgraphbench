#!/bin/sh
# install Amazon v2 dataset (https://cseweb.ucsd.edu/~jmcauley/datasets/amazon_v2/)
curl https://jmcauley.ucsd.edu/data/amazon_v2/categoryFilesSmall/Video_Games_5.json.gz --output video_games-5.zip
unzip video_games-5.zip -d amazon-video_games-5/
rm video_games-5.zip
curl https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_v2/metaFiles2/meta_Video_Games.json.gz --output metadata.zip
unzip metadata.zip -d amazon-video_games-5/
rm metadata.zip