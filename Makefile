ml-100k:
	python3 data_integration.py -d 'ml-100k' -i 'datasets/ml-100k' -o 'datasets/ml-100k/processed' \
		-w 16 -ci -cu -cr -map

ml-1m:
	python3 data_integration.py -d 'ml-1m' -i 'datasets/ml-1m' -o 'datasets/ml-1m/processed' \
		-w 16 -ci -cu -cr -map

lastfm:
	python3 data_integration.py -d 'lastfm' -i 'datasets/lastfm' -o 'datasets/lastfm/processed' \
		-w 32 -ci -cr -map

book-crossing:
	python3 data_integration.py -d 'book-crossing' -i 'datasets/book-crossing' -o 'datasets/book-crossing/processed' \
		-ci -map -w 16

steam:
	python3 data_integration.py -d 'steam' -i 'datasets/steam' -o 'datasets/steam/processed' \
		-ci -map -w 8