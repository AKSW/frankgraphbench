#!/bin/sh
# download coconut csv for enrichment of chembl dataset with natural products
curl https://coconut.s3.uni-jena.de/prod/downloads/2026-10/coconut_csv-10-2026.zip --output coconut_csv.zip
unzip coconut_csv.zip -d coconut # move it manually to the desired chembl version
rm coconut_csv.zip