#!/bin/sh
# install mind-small train dataset (https://msnews.github.io/)
# curl <YOUR WGET LINK FROM MSNEWS FOR MIND SMALL TRAIN> --output mind-small.zip
unzip mind-small.zip -d mind-small/
rm mind-small.zip