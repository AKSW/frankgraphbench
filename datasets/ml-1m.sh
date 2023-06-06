#!/bin/sh
wget https://files.grouplens.org/datasets/movielens/ml-1m.zip
if md5sum --status -c ml-1m.zip.md5; then
    echo "Checksum matched correctly!"
    unzip ml-1m.zip
    rm ml-1m.zip
else
    echo "Checksum doesn't match!"
    echo "Exiting...."
    exit 1
fi

