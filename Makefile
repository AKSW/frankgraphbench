# Mapping
ml-100k:
	python3 data_integration.py -d 'ml-100k' -i 'datasets/ml-100k' -o 'datasets/ml-100k/processed' \
		-ci -cu -cr -map -w 4 

ml-1m:
	python3 data_integration.py -d 'ml-1m' -i 'datasets/ml-1m' -o 'datasets/ml-1m/processed' \
		-ci -cu -cr -map -w 4 

lastfm:
	python3 data_integration.py -d 'lastfm' -i 'datasets/lastfm' -o 'datasets/lastfm/processed' \
		-ci -cr -map -w 4

book-crossing:
	python3 data_integration.py -d 'book-crossing' -i 'datasets/book-crossing' -o 'datasets/book-crossing/processed' \
		-ci -map -w 4

steam:
	python3 data_integration.py -d 'steam' -i 'datasets/steam' -o 'datasets/steam/processed' \
		-ci -map -w 4

	 
# Enriching
enrich_ml-100k:
	python3 data_integration.py -d 'ml-100k' -i 'datasets/ml-100k' -o 'datasets/ml-100k/processed' \
		-enrich -w 4

enrich_ml-1m:
	python3 data_integration.py -d 'ml-1m' -i 'datasets/ml-1m' -o 'datasets/ml-1m/processed' \
		-enrich -w 4

enrich_lastfm:
	python3 data_integration.py -d 'lastfm' -i 'datasets/lastfm' -o 'datasets/lastfm/processed' \
		-enrich -w 4
	