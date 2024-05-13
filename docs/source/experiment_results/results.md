# Results
Here we present the average and standard deviation results of previously ran experiments, and we point to the corresponding `.yml` configuration file so that users can consistently reproduce said experiment.

## ml-100k-enriched
Experiment ran using the MovieLens-100k dataset with the follwing presented models and their configurations. The complete configuration can be found in `config_files/run_ml-100k_enriched.yml`: 

- Summarized results from `experiment_results/ml-100k-enriched.csv`:

| Model | MAP@5 | nDCG@5 |
|---------|---------|-----------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.1833 ± .0086|.2354 ± .0109|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.1783 ± .0060|.2328 ± .0090|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.0046 ± .0004|.0073 ± .0007|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.0012 ± .0002|.0019 ± .0002|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.0033 ± .0002|.0053 ± .0006|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.0062 ± .0013|.0096 ± .0014|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.0041 ± .0007|.0063 ± .0010|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.0076 ± .0002|.0119 ± .0007|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.0038 ± .0004|.0060 ± .0006|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.0063 ± .0004|.0096 ± .0006|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.0065 ± .0006|.0102 ± .0007|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/distiluse-base-multilingual-cased-v2;embed_with=abstract;iterations=30;mi=0.5|.0028 ± .0004|.0046 ± .0006|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.1836 ± .0091|.2375 ± .0103|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 0.8, 'q': 0.6, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.1772 ± .0057|.2304 ± .0043|
|EPHEN based model + cosine similarity;embedding_model=transE;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 1, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0046 ± .0004|.0073 ± .0007|
|EPHEN based model + cosine similarity;embedding_model=transH;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0012 ± .0002|.0019 ± .0002|
|EPHEN based model + cosine similarity;embedding_model=transR;embedding_model_kwargs={'embedding_dim': 150, 'relation_dim': 90, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|.0033 ± .0002|.0053 ± .0006|
|EPHEN based model + cosine similarity;embedding_model=transD;embedding_model_kwargs={'embedding_dim': 150, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0062 ± .0013|.0096 ± .0014|
|EPHEN based model + cosine similarity;embedding_model=tuckER;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0041 ± .0007|.0063 ± .0010|
|EPHEN based model + cosine similarity;embedding_model=rESCAL;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0076 ± .0002|.0119 ± .0007|
|EPHEN based model + cosine similarity;embedding_model=distMult;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|.0038 ± .0004|.0060 ± .0006|
|EPHEN based model + cosine similarity;embedding_model=complEx;embedding_model_kwargs={'embedding_dim': 100, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0062 ± .0004|.0096 ± .0006|
|EPHEN based model + cosine similarity;embedding_model=rotatE;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|.0065 ± .0006|.0102 ± .0007|

- Summarized execution time results from `experiment_results/ml-100k-enriched_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|24.75 ± 1.211|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|25.73 ± 1.092|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|40.85 ± 2.265|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|70.55 ± 3.375|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|126.0 ± 1.904|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|78.69 ± 3.573|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|381.5 ± 3.296|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|59.49 ± 2.888|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|54.17 ± 2.435|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|46.09 ± 1.553|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|101.9 ± 2.870|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/distiluse-base-multilingual-cased-v2;embed_with=abstract;iterations=30;mi=0.5|94.67 ± 4.064|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|96.86 ± 1.099|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 0.8, 'q': 0.6, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|95.09 ± 1.554|
|EPHEN based model + cosine similarity;embedding_model=transE;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 1, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|112.8 ± 2.226|
|EPHEN based model + cosine similarity;embedding_model=transH;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|140.6 ± 3.690|
|EPHEN based model + cosine similarity;embedding_model=transR;embedding_model_kwargs={'embedding_dim': 150, 'relation_dim': 90, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|196.6 ± 2.413|
|EPHEN based model + cosine similarity;embedding_model=transD;embedding_model_kwargs={'embedding_dim': 150, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|148.4 ± 2.020|
|EPHEN based model + cosine similarity;embedding_model=tuckER;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|453.0 ± 4.003|
|EPHEN based model + cosine similarity;embedding_model=rESCAL;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|128.0 ± 2.684|
|EPHEN based model + cosine similarity;embedding_model=distMult;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|122.0 ± 3.137|
|EPHEN based model + cosine similarity;embedding_model=complEx;embedding_model_kwargs={'embedding_dim': 100, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|118.3 ± 2.574|
|EPHEN based model + cosine similarity;embedding_model=rotatE;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|178.9 ± 2.400|

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
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/distiluse-base-multilingual-cased-v2;embed_with=abstract;iterations=30;mi=0.5|.0165 ± .0002|.0247 ± .0002|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.1611 ± .0023|.2000 ± .0027|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 0.8, 'q': 0.6, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.1616 ± .0016|.2002 ± .0017|
|EPHEN based model + cosine similarity;embedding_model=transE;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 1, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0038 ± .0002|.0059 ± .0003|
|EPHEN based model + cosine similarity;embedding_model=transH;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0015 ± .0001|.0024 ± .0002|
|EPHEN based model + cosine similarity;embedding_model=transR;embedding_model_kwargs={'embedding_dim': 150, 'relation_dim': 90, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|.0007 ± .0001|.0012 ± .0002|
|EPHEN based model + cosine similarity;embedding_model=transD;embedding_model_kwargs={'embedding_dim': 150, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0023 ± .0002|.0036 ± .0003|
|EPHEN based model + cosine similarity;embedding_model=tuckER;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0002 ± .0001|.0003 ± .0001|
|EPHEN based model + cosine similarity;embedding_model=rESCAL;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0077 ± .0006|.0118 ± .0010|
|EPHEN based model + cosine similarity;embedding_model=distMult;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|.0019 ± .0006|.0027 ± .0008|
|EPHEN based model + cosine similarity;embedding_model=complEx;embedding_model_kwargs={'embedding_dim': 100, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0014 ± .0002|.0022 ± .0002|
|EPHEN based model + cosine similarity;embedding_model=rotatE;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|.0036 ± .0003|.0057 ± .0005|

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
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/distiluse-base-multilingual-cased-v2;embed_with=abstract;iterations=30;mi=0.5|568.8 ± 11.74|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|568.8 ± 11.83|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 0.8, 'q': 0.6, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|566.2 ± 27.50|
|EPHEN based model + cosine similarity;embedding_model=transE;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 1, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|924.1 ± 25.48|
|EPHEN based model + cosine similarity;embedding_model=transH;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|1238. ± 26.79|
|EPHEN based model + cosine similarity;embedding_model=transR;embedding_model_kwargs={'embedding_dim': 150, 'relation_dim': 90, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|1755. ± 28.44|
|EPHEN based model + cosine similarity;embedding_model=transD;embedding_model_kwargs={'embedding_dim': 150, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|1389. ± 23.46|
|EPHEN based model + cosine similarity;embedding_model=tuckER;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|4445. ± 73.74|
|EPHEN based model + cosine similarity;embedding_model=rESCAL;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|1100. ± 24.61|
|EPHEN based model + cosine similarity;embedding_model=distMult;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|947.4 ± 19.35|
|EPHEN based model + cosine similarity;embedding_model=complEx;embedding_model_kwargs={'embedding_dim': 100, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|988.9 ± 27.50|
|EPHEN based model + cosine similarity;embedding_model=rotatE;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|1808. ± 26.36|

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
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/distiluse-base-multilingual-cased-v2;embed_with=abstract;iterations=30;mi=0.5|.3661 ± .0337|.4425 ± .0468|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.5834 ± .0021|.6760 ± .0051|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 0.8, 'q': 0.6, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.5855 ± .0112|.6784 ± .0150|
|EPHEN based model + cosine similarity;embedding_model=transE;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 1, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.3991 ± .0030|.4803 ± .0066|
|EPHEN based model + cosine similarity;embedding_model=transH;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.3897 ± .0034|.4690 ± .0071|
|EPHEN based model + cosine similarity;embedding_model=transR;embedding_model_kwargs={'embedding_dim': 150, 'relation_dim': 90, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|.4033 ± .0029|.4856 ± .0062|
|EPHEN based model + cosine similarity;embedding_model=transD;embedding_model_kwargs={'embedding_dim': 150, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.4079 ± .0020|.4900 ± .0038|
|EPHEN based model + cosine similarity;embedding_model=tuckER;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.4099 ± .0024|.4914 ± .0050|
|EPHEN based model + cosine similarity;embedding_model=rESCAL;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.4087 ± .0031|.4895 ± .0057|
|EPHEN based model + cosine similarity;embedding_model=distMult;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|.4070 ± .0029|.4876 ± .0058|
|EPHEN based model + cosine similarity;embedding_model=complEx;embedding_model_kwargs={'embedding_dim': 100, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.4043 ± .0031|.4860 ± .0050|
|EPHEN based model + cosine similarity;embedding_model=rotatE;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|.4088 ± .0020|.4885 ± .0040|

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
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/distiluse-base-multilingual-cased-v2;embed_with=abstract;iterations=30;mi=0.5|43.82 ± 1.039|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|42.07 ± .5346|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 0.8, 'q': 0.6, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|42.21 ± .9659|
|EPHEN based model + cosine similarity;embedding_model=transE;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 1, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|88.44 ± 1.454|
|EPHEN based model + cosine similarity;embedding_model=transH;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|114.7 ± 2.543|
|EPHEN based model + cosine similarity;embedding_model=transR;embedding_model_kwargs={'embedding_dim': 150, 'relation_dim': 90, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|119.9 ± 1.713|
|EPHEN based model + cosine similarity;embedding_model=transD;embedding_model_kwargs={'embedding_dim': 150, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|123.1 ± 2.499|
|EPHEN based model + cosine similarity;embedding_model=tuckER;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|393.4 ± 5.449|
|EPHEN based model + cosine similarity;embedding_model=rESCAL;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|103.4 ± 3.480|
|EPHEN based model + cosine similarity;embedding_model=distMult;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|86.60 ± 3.058|
|EPHEN based model + cosine similarity;embedding_model=complEx;embedding_model_kwargs={'embedding_dim': 100, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|93.11 ± 2.143|
|EPHEN based model + cosine similarity;embedding_model=rotatE;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|94.59 ± 2.656|