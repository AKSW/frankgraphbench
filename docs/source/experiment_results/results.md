# Results
Here we present the average and standard deviation results of previously ran experiments, and we point to the corresponding `.yml` configuration file so that users can consistently reproduce said experiment.

## ml-100k-enriched
Experiment ran using the MovieLens-100k dataset with the follwing presented models and their configurations. The complete configuration can be found in `config_files/run_ml-100k_enriched.yml`: 

- Summarized results from `experiment_results/ml-100k-enriched.csv`:

| Model | MAP@5 | nDCG@5 |
|---------|---------|-----------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.1833 ± .0086|.2354 ± .0109|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.1783 ± .0060|.2328 ± .0090|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.0063 ± .0004|.0096 ± .0006|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.0038 ± .0004|.0060 ± .0006|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.0076 ± .0002|.0119 ± .0007|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.0065 ± .0006|.0102 ± .0007|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.0062 ± .0013|.0096 ± .0014|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.0046 ± .0004|.0073 ± .0007|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.0012 ± .0002|.0019 ± .0002|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.0033 ± .0002|.0053 ± .0006|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.0041 ± .0007|.0063 ± .0010|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/distiluse-base-multilingual-cased-v2;embed_with=abstract;iterations=30;mi=0.5|.0028 ± .0004|.0046 ± .0006|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.1836 ± .0091|.2375 ± .0103|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 0.8, 'q': 0.6, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.1772 ± .0057|.2304 ± .0043|
|EPHEN based model + cosine similarity;embedding_model=complEx;embedding_model_kwargs={'embedding_dim': 100, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0062 ± .0004|.0096 ± .0006|
|EPHEN based model + cosine similarity;embedding_model=distMult;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|.0038 ± .0004|.0060 ± .0006|
|EPHEN based model + cosine similarity;embedding_model=rESCAL;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0076 ± .0002|.0119 ± .0007|
|EPHEN based model + cosine similarity;embedding_model=rotatE;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|.0065 ± .0006|.0102 ± .0007|
|EPHEN based model + cosine similarity;embedding_model=transD;embedding_model_kwargs={'embedding_dim': 150, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0062 ± .0013|.0096 ± .0014|
|EPHEN based model + cosine similarity;embedding_model=transE;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 1, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0046 ± .0004|.0073 ± .0007|
|EPHEN based model + cosine similarity;embedding_model=transH;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0012 ± .0002|.0019 ± .0002|
|EPHEN based model + cosine similarity;embedding_model=transR;embedding_model_kwargs={'embedding_dim': 150, 'relation_dim': 90, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|.0033 ± .0002|.0053 ± .0006|
|EPHEN based model + cosine similarity;embedding_model=tuckER;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0041 ± .0007|.0063 ± .0010|

- Summarized execution time results from `experiment_results/ml-100k-enriched_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|24.75 ± 1.211|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|25.73 ± 1.092|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|46.09 ± 1.553|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|54.17 ± 2.435|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|59.49 ± 2.888|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|101.9 ± 2.870|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|78.69 ± 3.573|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|40.85 ± 2.265|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|70.55 ± 3.375|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|126.0 ± 1.904|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|381.5 ± 3.296|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/distiluse-base-multilingual-cased-v2;embed_with=abstract;iterations=30;mi=0.5|94.67 ± 4.064|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|96.86 ± 1.099|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 0.8, 'q': 0.6, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|95.09 ± 1.554|
|EPHEN based model + cosine similarity;embedding_model=complEx;embedding_model_kwargs={'embedding_dim': 100, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|118.3 ± 2.574|
|EPHEN based model + cosine similarity;embedding_model=distMult;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|122.0 ± 3.137|
|EPHEN based model + cosine similarity;embedding_model=rESCAL;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|128.0 ± 2.684|
|EPHEN based model + cosine similarity;embedding_model=rotatE;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|178.9 ± 2.400|
|EPHEN based model + cosine similarity;embedding_model=transD;embedding_model_kwargs={'embedding_dim': 150, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|148.4 ± 2.020|
|EPHEN based model + cosine similarity;embedding_model=transE;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 1, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|112.8 ± 2.226|
|EPHEN based model + cosine similarity;embedding_model=transH;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|140.6 ± 3.690|
|EPHEN based model + cosine similarity;embedding_model=transR;embedding_model_kwargs={'embedding_dim': 150, 'relation_dim': 90, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|196.6 ± 2.413|
|EPHEN based model + cosine similarity;embedding_model=tuckER;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|453.0 ± 4.003|

## ml-1m-enriched

Experiment ran using the MovieLens-1m dataset with the follwing presented models and their configurations. The complete configuration can be found in `config_files/run_ml-1m_enriched.yml`: 

- Summarized results from `experiment_results/ml-1m-enriched.csv`:

| Model | MAP@5 | nDCG@5 |
|---------|---------|-----------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.1612 ± .0014|.1999 ± .0018|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.1617 ± .0027|.2003 ± .0030|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.0015 ± .0001|.0022 ± .0002|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.0019 ± .0006|.0027 ± .0008|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.0077 ± .0006|.0118 ± .0010|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.0036 ± .0003|.0057 ± .0005|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.0023 ± .0002|.0036 ± .0003|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.0038 ± .0002|.0059 ± .0003|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.0015 ± .0001|.0024 ± .0002|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.0007 ± .0001|.0012 ± .0002|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.0002 ± .0001|.0003 ± .0001|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/distiluse-base-multilingual-cased-v2;embed_with=abstract;iterations=30;mi=0.5|.0165 ± .0002|.0247 ± .0002|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.1611 ± .0023|.2000 ± .0027|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 0.8, 'q': 0.6, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.1616 ± .0016|.2002 ± .0017|
|EPHEN based model + cosine similarity;embedding_model=complEx;embedding_model_kwargs={'embedding_dim': 100, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0014 ± .0002|.0022 ± .0002|
|EPHEN based model + cosine similarity;embedding_model=distMult;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|.0019 ± .0006|.0027 ± .0008|
|EPHEN based model + cosine similarity;embedding_model=rESCAL;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0077 ± .0006|.0118 ± .0010|
|EPHEN based model + cosine similarity;embedding_model=rotatE;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|.0036 ± .0003|.0057 ± .0005|
|EPHEN based model + cosine similarity;embedding_model=transD;embedding_model_kwargs={'embedding_dim': 150, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0023 ± .0002|.0036 ± .0003|
|EPHEN based model + cosine similarity;embedding_model=transE;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 1, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0038 ± .0002|.0059 ± .0003|
|EPHEN based model + cosine similarity;embedding_model=transH;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0015 ± .0001|.0024 ± .0002|
|EPHEN based model + cosine similarity;embedding_model=transR;embedding_model_kwargs={'embedding_dim': 150, 'relation_dim': 90, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|.0007 ± .0001|.0012 ± .0002|
|EPHEN based model + cosine similarity;embedding_model=tuckER;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|.0002 ± .0001|.0003 ± .0001|

- Summarized execution time results from `experiment_results/ml-1m-enriched_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|81.63 ± 2.760|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|73.49 ± 3.471|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|491.9 ± 25.50|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|463.7 ± 17.08|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|616.5 ± 25.47|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|1294. ± 19.58|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|889.6 ± 27.52|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|426.0 ± 19.07|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|732.3 ± 24.00|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|1256. ± 20.99|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|3926. ± 68.42|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/distiluse-base-multilingual-cased-v2;embed_with=abstract;iterations=30;mi=0.5|568.8 ± 11.74|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|568.8 ± 11.83|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 0.8, 'q': 0.6, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|566.2 ± 27.50|
|EPHEN based model + cosine similarity;embedding_model=complEx;embedding_model_kwargs={'embedding_dim': 100, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|988.9 ± 27.50|
|EPHEN based model + cosine similarity;embedding_model=distMult;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|947.4 ± 19.35|
|EPHEN based model + cosine similarity;embedding_model=rESCAL;embedding_model_kwargs={'embedding_dim': 50, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|1100. ± 24.61|
|EPHEN based model + cosine similarity;embedding_model=rotatE;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|1808. ± 26.36|
|EPHEN based model + cosine similarity;embedding_model=transD;embedding_model_kwargs={'embedding_dim': 150, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|1389. ± 23.46|
|EPHEN based model + cosine similarity;embedding_model=transE;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 1, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|924.1 ± 25.48|
|EPHEN based model + cosine similarity;embedding_model=transH;embedding_model_kwargs={'embedding_dim': 150, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|1238. ± 26.79|
|EPHEN based model + cosine similarity;embedding_model=transR;embedding_model_kwargs={'embedding_dim': 150, 'relation_dim': 90, 'scoring_fct_norm': 2, 'epochs': 25, 'seed': 42, 'triples': 'all'};embed_with=graph;iterations=30;mi=0.5|1755. ± 28.44|
|EPHEN based model + cosine similarity;embedding_model=tuckER;embedding_model_kwargs={'embedding_dim': 200, 'epochs': 25, 'seed': 42, 'triples': 'ratings'};embed_with=graph;iterations=30;mi=0.5|4445. ± 73.74|