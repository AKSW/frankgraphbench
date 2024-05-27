# Results
Here we present the average and standard deviation results of previously ran experiments, and we point to the corresponding `.yml` configuration file so that users can consistently reproduce said experiment.

## ml-100k-enriched
Experiment ran using the MovieLens-100k dataset with the follwing presented models and their configurations. The complete configuration can be found in `config_files/run_ml-100k_enriched.yml`: 

- Summarized results from `experiment_results/ml-100k-enriched.csv`:

| Model | MAP@5 | nDCG@5 |
|---------|---------|-----------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.1819 ± .0106|.2339 ± .0097|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.1775 ± .0096|.2301 ± .0088|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.0041 ± .0005|.0068 ± .0009|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.0010 ± .0003|.0056 ± .0007|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.0034 ± .0004|.0056 ± .0007|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.0063 ± .0008|.0101 ± .0010|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.0040 ± .0005|.0065 ± .0006|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.0079 ± .0011|.0124 ± .0019|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.0037 ± .0010|.0060 ± .0014|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.0065 ± .0009|.0106 ± .0014|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.0065 ± .0006|.0104 ± .0010|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|.0141 ± .0006|.0252 ± .0005|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.1812 ± .0078|.2338 ± .0076|

- Summarized execution time results from `experiment_results/ml-100k-enriched_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|26.31 ± 1.073|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|25.44 ± .7091|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|43.75 ± 1.923|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|72.83 ± 3.641|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|128.0 ± 2.616|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|79.85 ± 3.074|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|381.6 ± 3.547|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|60.83 ± 2.265|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|55.10 ± 2.484|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|46.26 ± 2.255|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|102.9 ± 1.780|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|177.4 ± 1.292|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|96.80 ± 1.006|

## ml-1m-enriched

Experiment ran using the MovieLens-1m dataset with the follwing presented models and their configurations. The complete configuration can be found in `config_files/run_ml-1m_enriched.yml`: 

- Summarized results from `experiment_results/ml-1m-enriched.csv`:

| Model | MAP@5 | nDCG@5 |
|---------|---------|-----------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.1625 ± .0021|.2014 ± .0026|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.1624 ± .0038|.2016 ± .0040|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.0041 ± .0002|.0063 ± .0002|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.0014 ± .0002|.0021 ± .0004|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.0008 ± .0001|.0012 ± .0001|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.0021 ± .0002|.0033 ± .0002|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.0003 ± .0001|.0003 ± .0001|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.0076 ± .0004|.0116 ± .0007|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.0020 ± .0006|.0029 ± .0008|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.0014 ± .0004|.0022 ± .0004|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.0034 ± .0002|.0055 ± .0002|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|.0020 ± .0002|.0030 ± .0001|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.1622 ± .0040|.2013 ± .0036|

- Summarized execution time results from `experiment_results/ml-1m-enriched_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|67.28 ± 2.997|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|74.52 ± 2.706|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|505.7 ± 136.6|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|834.3 ± 181.8|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|1404. ± 282.5|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|946.1 ± 112.5|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|4475. ± 1067.|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|648.5 ± 55.35|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|470.0 ± 19.09|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|490.4 ± 23.20|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|1289. ± 22.07|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|749.3 ± 6.818|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|549.0 ± 10.42|

## lastfm

Experiment ran using the Douban Movie dataset with the follwing presented models and their configurations. The complete configuration can be found in `config_files/run_lastfm-enriched.yml`:

- Summarized results from `experiment_results/lastfm-enriched.csv`:

| Model | MAP@5 | nDCG@5 |
|---------|---------|-----------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.1408 ± .0043|.1923 ± .0054|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.1390 ± .0035|.1946 ± .0035|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.0003 ± .0001|.0003 ± .0001|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.0002 ± .0002|.0002 ± .0003|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.0001 ± .0001|.0001 ± .0001|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.0002 ± .0001|.0003 ± .0001|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.0003 ± .0001|.0003 ± .0001|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.0002 ± .0001|.0002 ± .0001|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.0003 ± .0001|.0003 ± .0002|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.0002 ± .0001|.0003 ± .0002|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.0003 ± .0001|.0003 ± .0002|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|.0021 ± .0011|.0023 ± .0013|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.1383 ± .0017|.1903 ± .0026|

- Summarized execution time results from `experiment_results/lastfm-enriched_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|153.3 ± 1.309|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|155.9 ± 1.798|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|74.97 ± 18.59|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|112.3 ± 24.47|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|1767. ± 530.4|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|143.8 ± 30.80|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|513.9 ± 157.7|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|142.0 ± 34.93|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|213.1 ± 68.10|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|89.37 ± 21.57|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|951.5 ± 283.4|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|629.6 ± 30.63|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|348.0 ± 6.012|

## yelp

Experiment ran using the Yelp Challenge dataset with the follwing presented models and their configurations. The complete configuration can be found in `config_files/run_yelp.yml`: 

- Summarized results from `experiment_results/yelp.csv`:

| Model | MAP@10 | nDCG@10 |
|---------|---------|-----------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.01689 ± .00017|.03860 ± .00036|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.01688 ± .00029|.03852 ± .00078|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.00001 ± .00000|.00004 ± .00000|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.00010 ± .00001|.00026 ± .00003|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.00000 ± .00000|.00001 ± .00000|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.00001 ± .00000|.00003 ± .00000|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.00001 ± .00000|.00002 ± .00001|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.00006 ± .00001|.00017 ± .00002|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.00001 ± .00000|.00002 ± .00000|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.00002 ± .00000|.00007 ± .00001|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.00001 ± .00000|.00004 ± .00001|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|.00001 ± .00000|.00004 ± .00001|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.01683 ± .00015|.03858 ± .00059|

- Summarized execution time results from `experiment_results/yelp_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|1307.4 ± 333.51|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|1417.7 ± 555.66|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|6423.5 ± 1493.2|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|9996.2 ± 2948.8|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|28568. ± 7317.5|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|13663. ± 3201.2|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|15845. ± 140.81|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|3734.3 ± 163.13|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|7292.4 ± 215.27|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|6905.9 ± 406.81|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|41117. ± 231.11|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|8067.5 ± 75.832|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|4243.7 ± 139.98|

## douban-movie

Experiment ran using the Douban Movie dataset with the follwing presented models and their configurations. The complete configuration can be found in `config_files/run_douban-movie.yml`: 

- Summarized results from `experiment_results/douban-movie.csv`:

| Model | MAP@5 | nDCG@5 |
|---------|---------|-----------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.5843 ± .0101|.6754 ± .0117|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.5885 ± .0047|.6825 ± .0044|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.3991 ± .0032|.4813 ± .0064|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.3998 ± .0045|.4687 ± .0079|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.4036 ± .0018|.4855 ± .0044|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.4076 ± .0034|.4888 ± .0045|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.4095 ± .0024|.4903 ± .0052|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.4091 ± .0007|.4910 ± .0036|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.4067 ± .0019|.4877 ± .0044|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.4043 ± .0021|.4857 ± .0049|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.4091 ± .0024|.4882 ± .0066|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|.4517 ± .0078|.5284 ± .0045|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.5833 ± .0043|.6755 ± .0059|

- Summarized execution time results from `experiment_results/douban-movie_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|5.199 ± .6045|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|5.240 ± .1954|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|47.84 ± .6285|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|70.69 ± 1.761|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|78.39 ± 2.203|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|79.52 ± 3.933|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|348.6 ± 7.303|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|62.87 ± 2.368|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|44.91 ± 1.734|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|49.91 ± 2.109|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|51.02 ± 1.804|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|47.73 ± .6584|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|41.90 ± .5456|