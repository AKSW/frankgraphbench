# Results
Here we present the average and standard deviation results of the current benchmark version. We also point to the corresponding `.yml` configuration file used for each configuration so that users can consistently reproduce experiments or build new configurations based on one of them.

## ml-100k

Experiment ran using the MovieLens-100k dataset with the following presented models and their configurations. The complete configuration can be found in `config_files/run_ml-100k.yml`: 

- Summarized results from `experiment_results/fixed_db16_runs/ml-100k.csv` and `experiment_results/fixed_db16_runs/ml-100k_gnns.csv`:

| Model | MAP@10 | nDCG@10 |
|---------|----------|------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.0993 ± .0034|.1766 ± .0043|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.0973 ± .0039|.1748 ± .0064|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.0032 ± .0003|.0077 ± .0004|
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
|BPRMF;embed_size=64;epoch=1000;regs[1e-05, 1e-05, 0.01]|.2897 ± .0073|.3874 ± .0098|
|CFKG;n_layers=3;adj_type=si;adj_uni_type=sum;alg_typebi|.0652 ± .0029|.1227 ± .0034|
|CKE;epoch=1000;kge_size=64;embed_size=64;regs=[1e-05, 1e-05, 0.01];lr=0.0001|.2939 ± .0056|.3898 ± .0067|
|KGAT;n_layers=3;adj_type=si;adj_uni_type=sum;alg_typebi|.2690 ± .0021|.3649 ± .0029|

- Summarized execution time results from `experiment_results/fixed_db16_runs/ml-100k_times.csv` and `experiment_results/fixed_db16_runs/ml-100k_gnns_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

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
|BPRMF;embed_size=64;epoch=1000;regs[1e-05, 1e-05, 0.01]|2774. ± 460.9|
|CFKG;n_layers=3;adj_type=si;adj_uni_type=sum;alg_typebi|37254 ± 1163.|
|CKE;epoch=1000;kge_size=64;embed_size=64;regs=[1e-05, 1e-05, 0.01];lr=0.0001|3242. ± 266.1|
|KGAT;n_layers=3;adj_type=si;adj_uni_type=sum;alg_typebi|38941 ± 1146.|

## ml-100k_enriched

Experiment ran using the MovieLens-100k dataset with DBpedia enrichement and the following presented models and their configurations. The complete configuration can be found in `config_files/run_ml-100k_enriched.yml` and `config_files/run_ml-100k_enriched_gnns.yml`: 

- Summarized results from `experiment_results/fixed_db16_runs/ml-100k_enriched.csv`:

| Model | MAP@10 | nDCG@10 |
|---------|----------|------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.1439 ± .0016|.2349 ± .0019|
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
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-mpnet-base-v2;embed_with=abstract;iterations=30;mi=0.5|.0046 ± .0003|.0107 ± .0005|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.1442 ± .0022|.2350 ± .0019|
|Entity2Rec;embedding_model=deepwalk_based;embedding_model_kwargs={'config': {'save_weights': True}, 'parameters': {'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1}};run_all=False;workers=6;iterations=1;collab_only=False;content_only=False|.0056 ± .0013|.0136 ± .0028|
|BPRMF;embed_size=64;epoch=1000;regs[1e-05, 1e-05, 0.01]|.2887 ± .0036|.3852 ± .0049|
|CFKG;n_layers=3;adj_type=si;adj_uni_type=sum;alg_typebi|.0410 ± .0011|.0834 ± .0017|
|CKE;epoch=1000;kge_size=64;embed_size=64;regs=[1e-05, 1e-05, 0.01];lr=0.0001|.2915 ± .0048|.3880 ± .0068|
|KGAT;n_layers=3;adj_type=si;adj_uni_type=sum;alg_typebi|.2740 ± .0030|.3707 ± .0034|

- Summarized execution time results from `experiment_results/fixed_db16_runs/ml-100k_enriched_times.csv` and `experiment_results/fixed_db16_runs/ml-100k_enriched_gnns_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

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
|BPRMF;embed_size=64;epoch=1000;regs[1e-05, 1e-05, 0.01]|7498. ± 1095.|
|CFKG;n_layers=3;adj_type=si;adj_uni_type=sum;alg_typebi|54686 ± 1834.|
|CKE;epoch=1000;kge_size=64;embed_size=64;regs=[1e-05, 1e-05, 0.01];lr=0.0001|9050. ± 527.7|
|KGAT;n_layers=3;adj_type=si;adj_uni_type=sum;alg_typebi|52116 ± 4862.|

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
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-mpnet-base-v2;embed_with=abstract;iterations=30;mi=0.5|592.6 ± 5.611|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|520.1 ± 4.842|

## lastfm

Experiment ran using the Lastfm dataset with the following presented models and their configurations. The complete configuration can be found in `config_files/run_lastfm.yml`:

- Summarized results from `experiment_results/fixed_db16_runs/lastfm.csv` and `experiment_results/fixed_db16_runs/lastfm_gnns.csv`:

| Model | MAP@10 | nDCG@10 |
|---------|----------|------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.0741 ± .0017|.1753 ± .0042|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.0756 ± .0015|.1782 ± .0047|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.0001 ± .0000|.0002 ± .0001|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.0002 ± .0001|.0005 ± .0001|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.0001 ± .0000|.0002 ± .0001|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.0002 ± .0000|.0005 ± .0002|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.0002 ± .0001|.0004 ± .0001|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.0001 ± .0000|.0004 ± .0003|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.0001 ± .0000|.0003 ± .0002|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.0002 ± .0001|.0004 ± .0003|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.0002 ± .0000|.0005 ± .0002|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-mpnet-base-v2;embed_with=name;iterations=30;mi=0.5|.0002 ± .0000|.0005 ± .0002|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.0757 ± .0025|.1774 ± .0047|
|BPRMF;embed_size=64;epoch=1000;regs[1e-05, 1e-05, 0.01]|.1032 ± .0013|.2362 ± .0036|
|CFKG;n_layers=3;adj_type=si;adj_uni_type=sum;alg_typebi|.0031 ± .0026|.0094 ± .0073|
|CKE;epoch=1000;kge_size=64;embed_size=64;regs=[1e-05, 1e-05, 0.01];lr=0.0001|.1049 ± .0033|.2380 ± .0085|
|KGAT;n_layers=3;adj_type=si;adj_uni_type=sum;alg_typebi|.1017 ± .0021|.2342 ± .0032|

- Summarized execution time results from `experiment_results/fixed_db16_runs/lastfm_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|66.77 ± 1.416|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|64.84 ± 3.724|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|56.40 ± .6367|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|87.21 ± 1.854|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|449.6 ± 2.516|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|111.0 ± 1.613|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|381.7 ± 2.037|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|104.8 ± 2.123|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|53.39 ± 1.559|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|63.46 ± 1.600|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|153.0 ± 2.265|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-mpnet-base-v2;embed_with=name;iterations=30;mi=0.5|262.9 ± .5831|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|144.7 ± 1.818|

- Summarized execution time results from `experiment_results/fixed_db16_runs/lastfm_gnns_times.csv` (configuration: CPU: Apple M3 Ultra; RAM: 256GB; GPUs: []):

| Model | Execution Time (s) |
|---------|----------------------|
|BPRMF;embed_size=64;epoch=1000;regs[1e-05, 1e-05, 0.01]|1883. ± 72.75|
|CFKG;n_layers=3;adj_type=si;adj_uni_type=sum;alg_typebi|7920. ± 67.19|
|CKE;epoch=1000;kge_size=64;embed_size=64;regs=[1e-05, 1e-05, 0.01];lr=0.0001|2537. ± 373.2|
|KGAT;n_layers=3;adj_type=si;adj_uni_type=sum;alg_typebi|19364 ± 1473.|

## lastfm_enriched

Experiment ran using the Lastfm dataset with DBpedia enrichement and the following presented models and their configurations. The complete configuration can be found in `config_files/run_lastfm-enriched.yml`:

- Summarized results from `experiment_results/fixed_db16_runs/lastfm_enriched.csv` and `experiment_results/fixed_db16_runs/lastfm_enriched_gnns.csv`:

| Model | MAP@10 | nDCG@10 |
|---------|----------|------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.0840 ± .0021|.1988 ± .0036|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.0839 ± .0021|.2000 ± .0040|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.0001 ± .0001|.0004 ± .0002|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.0002 ± .0001|.0004 ± .0003|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.0001 ± .0000|.0001 ± .0000|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.0001 ± .0001|.0002 ± .0002|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.0001 ± .0000|.0003 ± .0001|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.0002 ± .0001|.0004 ± .0001|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.0002 ± .0001|.0005 ± .0002|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.0002 ± .0000|.0004 ± .0001|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.0002 ± .0000|.0004 ± .0002|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-mpnet-base-v2;embed_with=abstract;iterations=30;mi=0.5|.0001 ± .0000|.0002 ± .0001|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.0840 ± .0010|.1992 ± .0022|
|BPRMF;embed_size=64;epoch=1000;regs[1e-05, 1e-05, 0.01]|.1035 ± .0027|.2392 ± .0035|
|CFKG;n_layers=3;adj_type=si;adj_uni_type=sum;alg_typebi|.0015 ± .0011|.0045 ± .0030|
|CKE;epoch=1000;kge_size=64;embed_size=64;regs=[1e-05, 1e-05, 0.01];lr=0.0001|.1035 ± .0030|.2394 ± .0043|
|KGAT;n_layers=3;adj_type=si;adj_uni_type=sum;alg_typebi|.1005 ± .0043|.2327 ± .0099|

- Summarized execution time results from `experiment_results/fixed_db16_runs/lastfm_enriched_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|171.7 ± 4.597|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|169.2 ± 2.115|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|69.51 ± 3.929|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|97.41 ± 3.335|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|1355. ± 4.618|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|122.5 ± 2.912|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|392.8 ± 3.085|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|116.9 ± 4.735|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|164.4 ± 6.892|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|75.28 ± 4.570|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|748.9 ± 3.893|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-roberta-large-v1;embed_with=abstract;iterations=30;mi=0.5|450.5 ± 1.035|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|368.2 ± 6.358|

- Summarized execution time results from `experiment_results/fixed_db16_runs/lastfm_enriched_gnns_times.csv` (configuration: CPU: Apple M3 Ultra; RAM: 256GB; GPUs: []):

| Model | Execution Time (s) |
|---------|----------------------|
|BPRMF;embed_size=64;epoch=1000;regs[1e-05, 1e-05, 0.01]|6039. ± 103.1|
|CFKG;n_layers=3;adj_type=si;adj_uni_type=sum;alg_typebi|22985 ± 317.9|
|CKE;epoch=1000;kge_size=64;embed_size=64;regs=[1e-05, 1e-05, 0.01];lr=0.0001|8218. ± 92.23|
|KGAT;n_layers=3;adj_type=si;adj_uni_type=sum;alg_typebi|57487 ± 8615.|

## douban-movie

Experiment ran using the Douban Movie dataset with the following presented models and their configurations. The complete configuration can be found in `config_files/run_douban-movie.yml`: 

- Summarized results from `experiment_results/fixed_db16_runs/douban-movie.csv`:

| Model | MAP@10 | nDCG@10 |
|---------|----------|------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.7416 ± .0080|.8109 ± .0065|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.7418 ± .0069|.8119 ± .0060|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.5839 ± .0049|.6737 ± .0032|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.5773 ± .0030|.6663 ± .0016|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.5900 ± .0041|.6784 ± .0021|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.5909 ± .0038|.6798 ± .0022|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.5927 ± .0052|.6800 ± .0027|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.5929 ± .0058|.6809 ± .0035|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.5915 ± .0033|.6781 ± .0014|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.5877 ± .0028|.6776 ± .0022|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.5911 ± .0036|.6792 ± .0022|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-mpnet-base-v2;embed_with=name_EN;iterations=30;mi=0.5|.5925 ± .0035|.6586 ± .0018|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.7401 ± .0046|.8086 ± .0042|
|Entity2Rec;embedding_model=deepwalk_based;embedding_model_kwargs={'config': {'save_weights': True}, 'parameters': {'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1}};run_all=False;workers=6;iterations=1;collab_only=False;content_only=False|.5956 ± .0134|.6846 ± .0089|

- Summarized execution time results from `experiment_results/fixed_db16_runs/douban-movie_times.csv` (configuration: CPU: AMD EPYC 7502P 32-Core Processor; RAM: 94GB; GPUs: ['NVIDIA A2']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|834.3 ± 24.82|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|823.1 ± 29.22|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|110.7 ± 1.628|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|126.1 ± 3.252|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|140.5 ± 4.679|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|134.4 ± 5.008|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|404.2 ± 8.478|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|117.1 ± 4.573|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|103.4 ± 3.690|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|105.7 ± 4.065|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|117.3 ± 3.828|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-mpnet-base-v2;embed_with=name_EN;iterations=30;mi=0.5|1099. ± 2.803|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|1488. ± 13.74|
|Entity2Rec;embedding_model=deepwalk_based;embedding_model_kwargs={'config': {'save_weights': True}, 'parameters': {'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1}};run_all=False;workers=6;iterations=1;collab_only=False;content_only=False|6276. ± 160.6|

## douban-movie_enriched

Experiment ran using the Douban Movie dataset with DBpedia enrichement and the following presented models and their configurations. The complete configuration can be found in `config_files/run_douban-movie_enriched.yml`: 

- Summarized results from `experiment_results/fixed_db16_runs/douban-movie_enriched.csv`:

| Model | MAP@10 | nDCG@10 |
|---------|----------|------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|.7371 ± .0064|.8043 ± .0060|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|.7367 ± .0050|.8039 ± .0048|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|.5838 ± .0046|.6738 ± .0038|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|.5777 ± .0029|.6669 ± .0025|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|.5891 ± .0041|.6780 ± .0022|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|.5913 ± .0032|.6799 ± .0015|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|.5930 ± .0036|.6808 ± .0015|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|.5935 ± .0049|.6819 ± .0030|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|.5917 ± .0049|.6783 ± .0019|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|.5874 ± .0042|.6774 ± .0020|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|.5912 ± .0044|.6796 ± .0019|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-mpnet-base-v2;embed_with=abstract;iterations=30;mi=0.5|.5283 ± .0032|.6225 ± .0019|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|.7372 ± .0044|.8044 ± .0047|
|Entity2Rec;embedding_model=deepwalk_based;embedding_model_kwargs={'config': {'save_weights': True}, 'parameters': {'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1}};run_all=False;workers=6;iterations=1;collab_only=False;content_only=False|.5944 ± .0089|.6829 ± .0081|

- Summarized execution time results from `experiment_results/fixed_db16_runs/douban-movie_times_enriched.csv` (configuration: CPU: AMD Ryzen 5 7600 6-Core Processor; RAM: 31GB; GPUs: ['NVIDIA GeForce RTX 4060']):

| Model | Execution Time (s) |
|---------|----------------------|
|Node2Vec based model + cosine similarity;q=1.0;p=1.0;embedding_size=64|832.9 ± 15.72|
|Node2Vec based model + cosine similarity;q=0.6;p=0.8;embedding_size=64|856.7 ± 12.74|
|TransE based model + cosine similarity;embedding_dim=150;scoring_fct_norm=1;epochs=25;seed=42;triples=ratings|112.4 ± 4.230|
|TransH based model + cosine similarity;embedding_dim=150;scoring_fct_norm=2;epochs=25;seed=42;triples=ratings|129.6 ± 5.001|
|TransR based model + cosine similarity;embedding_dim=150;relation_dim=90;scoring_fct_norm=2;epochs=25;seed=42;triples=all|144.0 ± 5.130|
|TransD based model + cosine similarity;embedding_dim=150;epochs=25;seed=42;triples=ratings|138.6 ± 5.678|
|TuckER based model + cosine similarity;embedding_dim=200;dropout_0=0.3;dropout_1=0.4;dropout_2=0.5;apply_batch_normalization=True;epochs=25;seed=42;triples=ratings|406.2 ± 9.683|
|RESCAL based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=ratings|120.4 ± 5.355|
|DistMult based model + cosine similarity;embedding_dim=50;epochs=25;seed=42;triples=all|106.0 ± 4.017|
|ComplEx based model + cosine similarity;embedding_dim=100;epochs=25;seed=42|108.0 ± 4.924|
|RotatE based model + cosine similarity;embedding_dim=200;epochs=25;seed=42;triples=all|120.9 ± 5.727|
|EPHEN based model + cosine similarity;embedding_model=sentence-transformers/all-mpnet-base-v2;embed_with=abstract;iterations=30;mi=0.5|1114. ± 7.497|
|EPHEN based model + cosine similarity;embedding_model=deepwalk_based;embedding_model_kwargs={'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1};embed_with=graph;iterations=30;mi=0.5|1470. ± 16.06|
|Entity2Rec;embedding_model=deepwalk_based;embedding_model_kwargs={'config': {'save_weights': True}, 'parameters': {'walk_len': 10, 'p': 1.0, 'q': 1.0, 'n_walks': 50, 'embedding_size': 64, 'epochs': 1}};run_all=False;workers=6;iterations=1;collab_only=False;content_only=False|6278. ± 167.4|