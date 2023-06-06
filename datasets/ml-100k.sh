#!/bin/sh
wget https://files.grouplens.org/datasets/movielens/ml-100k.zip
if md5sum --status -c ml-100k.zip.md5; then
    echo "Checksum matched correctly!"
    unzip ml-100k.zip
    rm ml-100k.zip
else
    echo "Checksum doesn't match!"
    echo "Exiting...."
    exit 1
fi

