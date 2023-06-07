ml-100k:
	python3 data_integration.py -d 'ml-100k' -i 'datasets/ml-100k' -o 'datasets/ml-100k/processed' \
		-ci -cu -cr -map

ml-1m:
	python3 data_integration.py -d 'ml-1m' -i 'datasets/ml-1m' -o 'datasets/ml-1m/processed' \
		-ci -cu -cr -map

lastfm:
	python3 data_integration.py -d 'lastfm' -i 'datasets/lastfm' -o 'datasets/lastfm/processed' \
		-ci -map