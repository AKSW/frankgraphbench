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

- Summarized execution time results from `experiment_results/ml-100k-enriched_times.csv`: