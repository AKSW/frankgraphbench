#!/bin/sh
# install LastFM (HetRec 2011)
wget https://files.grouplens.org/datasets/hetrec2011/hetrec2011-lastfm-2k.zip
unzip hetrec2011-lastfm-2k.zip -d lastfm/
rm hetrec2011-lastfm-2k.zip