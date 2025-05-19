# Results
Here we present the average and standard deviation results of the current benchmark version. We also point to the corresponding `.yml` configuration file used for each configuration so that users can consistently reproduce experiments or build new configurations based on one of them.

## ml-100k

Experiment ran using the MovieLens-100k dataset with the following presented models and their configurations. The complete configuration can be found in `config_files/run_ml-100k.yml`: 

- Summarized results from `experiment_results/fixed_db16_runs/ml-100k.csv`:

| Model | MAP@10 | nDCG@10 |
|---------|----------|------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.0993 ± .0034|.1766 ± .0043|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.0973 ± .0039|.1748 ± .0064|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.0032 ± .0003|.0023 ± .0004|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.0009 ± .0003|.0023 ± .0004|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.0029 ± .0003|.0070 ± .0006|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.0047 ± .0003|.0113 ± .0005|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.0031 ± .0004|.0074 ± .0005|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.0051 ± .0003|.0120 ± .0007|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.0045 ± .0006|.0109 ± .0013|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.0048 ± .0010|.0113 ± .0015|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.0042 ± .0003|.0103 ± .0007|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-mpnet-base-v2;embed_with=movie_title;iterations=30;mi=0.5|.0017 ± .0003|.0039 ± .0005|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.0985 ± .0041|.1761 ± .0058|
|Entity2Rec;embedding_model=deepwalk_based;embedding_model_kwargs={'config': {'save_weights': True}, 'parameters': {'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1}};run_all=False;workers=6;iterations=1;collab_only=False;content_only=False|.0069 ± .0004|.0158 ± .0006|

- Summarized execution time results from `experiment_results/fixed_db16_runs/ml-100k_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|8.178 ± .1823|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|7.370 ± .6110|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|40.99 ± .3187|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|66.84 ± 1.996|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|79.29 ± 2.058|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|75.79 ± 2.347|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|382.2 ± 2.905|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|57.97 ± 2.069|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|39.87 ± 1.691|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|44.04 ± 1.478|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|47.50 ± 1.706|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-mpnet-base-v2;embed_with=movie_title;iterations=30;mi=0.5|66.40 ± .0470|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|50.83 ± .6383|
|Entity2Rec;embedding_model=deepwalk_based;embedding_model_kwargs={'config': {'save_weights': True}, 'parameters': {'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1}};run_all=False;workers=6;iterations=1;collab_only=False;content_only=False|74104 ± 3749.|

## ml-100k_enriched

Experiment ran using the MovieLens-100k dataset with DBpedia enrichement and the following presented models and their configurations. The complete configuration can be found in `config_files/run_ml-100k_enriched.yml`: 

- Summarized results from `experiment_results/fixed_db16_runs/ml-100k_enriched.csv`:

| Model | MAP@10 | nDCG@10 |
|---------|----------|------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.1434 ± .0015|.2349 ± .0019|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.1433 ± .0033|.2329 ± .0037|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.0033 ± .0002|.0082 ± .0003|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.0007 ± .0001|.0018 ± .0002|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.0022 ± .0004|.0058 ± .0009|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.0044 ± .0003|.0106 ± .0003|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.0029 ± .0005|.0070 ± .0009|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.0050 ± .0004|.0122 ± .0008|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.0033 ± .0008|.0081 ± .0018|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.0046 ± .0005|.0112 ± .0008|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.0045 ± .0003|.0108 ± .0008|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-mpnet-base-v2;embed_with=abstract;iterations=30;mi=0.5|.0045 ± .0003|.0108 ± .0008|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.1442 ± .0022|.2350 ± .0019|
|Entity2Rec;embedding_model=deepwalk_based;embedding_model_kwargs={'config': {'save_weights': True}, 'parameters': {'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1}};run_all=False;workers=6;iterations=1;collab_only=False;content_only=False|.0056 ± .0013|.0136 ± .0028|

- Summarized execution time results from `experiment_results/fixed_db16_runs/ml-100k_enriched_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|21.69 ± .2804|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|21.95 ± .6008|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|42.86 ± .8906|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|71.26 ± 1.692|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|113.8 ± 1.304|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|80.22 ± .9842|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|384.1 ± 2.356|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|62.31 ± .6928|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|52.90 ± 1.164|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|46.75 ± 1.562|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|86.69 ± 1.153|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-mpnet-base-v2;embed_with=abstract;iterations=30;mi=0.5|108.0 ± 1.952|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|85.93 ± .7969|
|Entity2Rec;embedding_model=deepwalk_based;embedding_model_kwargs={'config': {'save_weights': True}, 'parameters': {'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1}};run_all=False;workers=6;iterations=1;collab_only=False;content_only=False|75651 ± 2808.|

## ml-1m

Experiment ran using the MovieLens-1m dataset with the following presented models and their configurations. The complete configuration can be found in `config_files/run_ml-1m.yml`: 

- Summarized results from `experiment_results/fixed_db16_runs/ml-1m.csv`:

| Model | MAP@10 | nDCG@10 |
|---------|----------|------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.0846 ± .0017|.1449 ± .0024|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.0846 ± .0010|.1454 ± .0011|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.0026 ± .0001|.0063 ± .0003|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.0009 ± .0001|.0021 ± .0001|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.0007 ± .0001|.0016 ± .0002|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.0014 ± .0001|.0036 ± .0003|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.0002 ± .0001|.0003 ± .0001|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.0050 ± .0001|.0115 ± .0001|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.0010 ± .0002|.0025 ± .0005|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.0012 ± .0004|.0030 ± .0010|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.0025 ± .0001|.0062 ± .0004|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-mpnet-base-v2;embed_with=movie_title;iterations=30;mi=0.5|.0028 ± .0002|.0062 ± .0004|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.0843 ± .0011|.1445 ± .0017|

- Summarized execution time results from `experiment_results/fixed_db16_runs/ml-1m_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|31.10 ± .2524|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|33.11 ± 2.733|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|423.6 ± 17.24|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|715.0 ± 15.18|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|864.0 ± 16.52|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|858.0 ± 16.76|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|3888. ± 29.29|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|588.1 ± 22.05|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|398.2 ± 19.76|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|472.00 ± 20.89|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|693.2 ± 21.37|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-mpnet-base-v2;embed_with=movie_title;iterations=30;mi=0.5|499.3 ± 8.566|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|451.9 ± 6.538|

## ml-1m_enriched

Experiment ran using the MovieLens-1m dataset with DBpedia enrichement and the following presented models and their configurations. The complete configuration can be found in `config_files/run_ml-1m_enriched.yml`: 

- Summarized results from `experiment_results/fixed_db16_runs/ml-1m_enriched.csv`:

| Model | MAP@10 | nDCG@10 |
|---------|----------|------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.1254 ± .0018|.1961 ± .0026|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.1253 ± .0042|.1957 ± .0048|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.0027 ± .0002|.0065 ± .0005|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.0010 ± .0001|.0023 ± .0001|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.0005 ± .0001|.0013 ± .0002|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.0015 ± .0001|.0037 ± .0002|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.0002 ± .0001|.0004 ± .0001|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.0051 ± .0001|.0116 ± .0003|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.0027 ± .0002|.0066 ± .0005|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.0009 ± .0002|.0024 ± .0006|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.0024 ± .0001|.0066 ± .0005|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-mpnet-base-v2;embed_with=abstract;iterations=30;mi=0.5|.0019 ± .0003|.0044 ± .0004|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.1252 ± .0017|.1964 ± .0020|

- Summarized execution time results from `experiment_results/fixed_db16_runs/ml-1m_enriched_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|62.50 ± 3.393|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|65.73 ± 5.698|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|428.7 ± 8.749|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|718.4 ± 7.618|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|1114. ± 14.14|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|855.1 ± 13.96|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|3907. ± 15.04|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|594.5 ± 16.06|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|448.9 ± 13.98|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|476.3 ± 14.38|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|1127. ± 15.99|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|592.6 ± 5.611|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|520.1 ± 4.842|

## lastfm

Experiment ran using the Lastfm dataset with the following presented models and their configurations. The complete configuration can be found in `config_files/run_lastfm.yml`:

- Summarized results from `experiment_results/fixed_db16_runs/lastfm.csv`:

| Model | MAP@10 | nDCG@10 |
|---------|----------|------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.1171 ± .0034|.1628 ± .0054|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.1178 ± .0018|.1621 ± .0027|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.0003 ± .0001|.0003 ± .0001|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.0002 ± .0001|.0002 ± .0002|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.0002 ± .0001|.0003 ± .0002|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.0002 ± .0001|.0003 ± .0001|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.0002 ± .0001|.0004 ± .0001|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.0002 ± .0001|.0004 ± .0002|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.0003 ± .0002|.0003 ± .0002|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.0003 ± .0001|.0004 ± .0001|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.0003 ± .0001|.0003 ± .0002|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|.0001 ± .0000|.0001 ± .0000|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.1174 ± .0021|.1624 ± .0043|

- Summarized execution time results from `experiment_results/fixed_db16_runs/lastfm_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|65.50 ± 1.855|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|63.40 ± 3.157|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|60.20 ± 1.085|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|90.59 ± 2.066|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|453.1 ± 4.384|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|113.7 ± 2.467|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|384.5 ± 2.255|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|108.8 ± 2.364|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|55.70 ± 2.296|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|66.67 ± 2.371|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|155.3 ± 1.722|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|438.8 ± .7641|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|143.9 ± 2.147|

## lastfm_enriched

Experiment ran using the Lastfm dataset with DBpedia enrichement and the following presented models and their configurations. The complete configuration can be found in `config_files/run_lastfm-enriched.yml`:

- Summarized results from `experiment_results/fixed_db16_runs/lastfm_enriched.csv`:

| Model | MAP@10 | nDCG@10 |
|---------|----------|------------|
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

- Summarized execution time results from `experiment_results/fixed_db16_runs/lastfm_enriched_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

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

## douban-movie

Experiment ran using the Douban Movie dataset with the following presented models and their configurations. The complete configuration can be found in `config_files/run_douban-movie.yml`: 

- Summarized results from `experiment_results/fixed_db16_runs/douban-movie.csv`:

| Model | MAP@10 | nDCG@10 |
|---------|----------|------------|
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
|Entity2Rec;embedding_model=deepwalk_based;embedding_model_kwargs={'config': {'save_weights': True}, 'parameters': {'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1}};run_all=False;workers=6;iterations=1;collab_only=False;content_only=False|.4142 ± .0084|.4971 ± .0120|

- Summarized execution time results from `experiment_results/fixed_db16_runs/douban-movie_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

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
|Entity2Rec;embedding_model=deepwalk_based;embedding_model_kwargs={'config': {'save_weights': True}, 'parameters': {'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1}};run_all=False;workers=6;iterations=1;collab_only=False;content_only=False|9479. ± 301.5|

## douban-movie_enriched

Experiment ran using the Douban Movie dataset with DBpedia enrichement and the following presented models and their configurations. The complete configuration can be found in `config_files/run_douban-movie_enriched.yml`: 

- Summarized results from `experiment_results/fixed_db16_runs/douban-movie_enriched.csv`:

| Model | MAP@10 | nDCG@10 |
|---------|----------|------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.5739 ± .0093|.6627 ± .0134|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.5722 ± .0055|.6609 ± .0084|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.4035 ± .0029|.4830 ± .0044|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.3949 ± .0029|.4695 ± .0056|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.4062 ± .0022|.4872 ± .0066|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.4076 ± .0033|.4883 ± .0040|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.4045 ± .0032|.4866 ± .0055|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.4102 ± .0056|.4916 ± .0036|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.4011 ± .0011|.4810 ± .0040|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.4056 ± .0037|.4871 ± .0062|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.4086 ± .0016|.4895 ± .0028|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|.3876 ± .0038|.4601 ± .0036|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.5736 ± .0018|.6617 ± .0061|
|Entity2Rec;embedding_model=deepwalk_based;embedding_model_kwargs={'config': {'save_weights': True}, 'parameters': {'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1}};run_all=False;workers=6;iterations=1;collab_only=False;content_only=False|.4184 ± .0137|.5016 ± .0119|

- Summarized execution time results from `experiment_results/fixed_db16_runs/douban-movie_times_enriched.csv` (configuration: CPU: AMD Ryzen 5 7600 6-Core Processor; RAM: 31GB; GPUs: ['NVIDIA GeForce RTX 4060']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|2.824 ± .5424|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|2.839 ± .2007|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|58.86 ± 1.623|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|81.12 ± 1.741|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|95.10 ± 2.397|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|92.93 ± 2.962|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|160.5 ± 3.752|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|58.57 ± 2.213|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|46.99 ± 2.122|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|51.79 ± 2.264|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|56.15 ± 2.132|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|51.79 ± 43.51|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|22.54 ± 1.364|
|Entity2Rec;embedding_model=deepwalk_based;embedding_model_kwargs={'config': {'save_weights': True}, 'parameters': {'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1}};run_all=False;workers=6;iterations=1;collab_only=False;content_only=False|9266. ± 104.2|