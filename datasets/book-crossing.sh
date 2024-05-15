#!/bin/sh
# install Book Crossing
#curl <GET the download link from kaggle (https://www.kaggle.com/datasets/somnambwl/bookcrossing-dataset?resource=download)> --output BX-CSV-Dump.zip
unzip BX-CSV-Dump.zip -d book-crossing/
rm BX-CSV-Dump.zip
