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
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.1612 ± .0014|.1999 ± .0018|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.1617 ± .0027|.2003 ± .0030|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.0038 ± .0002|.0059 ± .0003|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.0015 ± .0001|.0024 ± .0002|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.0007 ± .0001|.0012 ± .0002|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.0023 ± .0002|.0036 ± .0003|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.0002 ± .0001|.0003 ± .0001|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.0077 ± .0006|.0118 ± .0010|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.0019 ± .0006|.0027 ± .0008|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.0015 ± .0001|.0022 ± .0002|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.0036 ± .0003|.0057 ± .0005|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|.0028 ± .0004|.0046 ± .0006|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.1611 ± .0023|.2000 ± .0027|

- Summarized execution time results from `experiment_results/ml-1m-enriched_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|81.63 ± 2.760|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|73.49 ± 3.471|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|426.0 ± 19.07|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|732.3 ± 24.00|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|1256. ± 20.99|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|889.6 ± 27.52|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|3926. ± 68.42|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|616.5 ± 25.47|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|463.7 ± 17.08|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|491.9 ± 25.50|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|1294. ± 19.58|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|.0028 ± .0004|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|568.8 ± 11.83|

## douban-movie

Experiment ran using the Douban Movie dataset with the follwing presented models and their configurations. The complete configuration can be found in `config_files/run_douban-movie.yml`: 

- Summarized results from `experiment_results/douban-movie.csv`:

| Model | MAP@5 | nDCG@5 |
|---------|---------|-----------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.5898 ± .0075|.6831 ± .0109|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.5841 ± .0053|.6772 ± .0052|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.3991 ± .0030|.4803 ± .0066|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.3900 ± .0034|.4690 ± .0071|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.4033 ± .0029|.4856 ± .0062|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.4079 ± .0020|.4900 ± .0038|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.4099 ± .0024|.4914 ± .0050|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.4087 ± .0031|.4895 ± .0057|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.4070 ± .0029|.4876 ± .0058|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.4044 ± .0033|.4863 ± .0049|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.4088 ± .0020|.4885 ± .0040|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|.0028 ± .0004|.0046 ± .0006|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.5834 ± .0021|.6760 ± .0051|

- Summarized execution time results from `experiment_results/douban-movie_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|4.305 ± .4799|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|5.825 ± .2634|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|49.61 ± 2.179|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|75.09 ± 3.026|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|82.42 ± 3.011|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|84.57 ± 3.652|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|352.4 ± 6.494|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|66.25 ± 1.970|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|48.70 ± 1.934|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|54.58 ± 2.171|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|54.62 ± 2.834|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|.0028 ± .0004|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|42.07 ± .5346|