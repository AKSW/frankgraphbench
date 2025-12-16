'''
Created on Dec 18, 2018
Tensorflow Implementation of Knowledge Graph Attention Network (KGAT) model in:
Wang Xiang et al. KGAT: Knowledge Graph Attention Network for Recommendation. In KDD 2019.
@author: Xiang Wang (xiangwang@u.nus.edu)
@modifiedBy: Paulo do Carmo on Dec, 2025
'''
import framework.recommender.models.kGAT.metrics as metrics
import multiprocess
import heapq
import numpy as np

cores = multiprocess.cpu_count() // 2

def ranklist_by_heapq(test_items, rating, Ks):
    item_score = {}
    for i in test_items:
        item_score[i] = rating[i]

    K_max = max(Ks)
    K_max_item_score = heapq.nlargest(K_max, item_score, key=item_score.get)

    auc = 0.
    return K_max_item_score, auc

def get_auc(item_score, user_pos_test):
    item_score = sorted(item_score.items(), key=lambda kv: kv[1])
    item_score.reverse()
    item_sort = [x[0] for x in item_score]
    posterior = [x[1] for x in item_score]

    r = []
    for i in item_sort:
        if i in user_pos_test:
            r.append(1)
        else:
            r.append(0)
    auc = metrics.auc(ground_truth=r, prediction=posterior)
    return auc

def ranklist_by_sorted(user_pos_test, test_items, rating, Ks):
    item_score = {}
    for i in test_items:
        item_score[i] = rating[i]

    K_max = max(Ks)
    K_max_item_score = heapq.nlargest(K_max, item_score, key=item_score.get)

    auc = get_auc(item_score, user_pos_test)
    return K_max_item_score, auc


def get_performance(user_pos_test, r, auc, Ks):
    precision, recall, ndcg, hit_ratio = [], [], [], []

    rank_hits = []
    for i in r:
        if i in user_pos_test:
            rank_hits.append(1)
        else:
            rank_hits.append(0)

    for K in Ks:
        precision.append(metrics.precision_at_k(rank_hits, K))
        recall.append(metrics.recall_at_k(rank_hits, K, len(user_pos_test)))
        ndcg.append(metrics.ndcg_at_k(rank_hits, K))
        hit_ratio.append(metrics.hit_at_k(rank_hits, K))

    return {'recall': np.array(recall), 'precision': np.array(precision),
            'ndcg': np.array(ndcg), 'hit_ratio': np.array(hit_ratio), 'auc': auc}


def test_one_user(x):
    user_wrap, data_generator, args = x
    # user u's ratings for user u and uid
    rating, u = user_wrap
    print(f"testing user {u}", end="; ", flush=True)
    try:
        training_items = data_generator.train_user_dict[u]
    except Exception:
        training_items = []
    #user u's items in the test set
    user_pos_test = data_generator.test_user_dict[u]

    test_items = list(data_generator.all_items - set(training_items))

    if args.test_flag == 'part':
        r, auc = ranklist_by_heapq(test_items, rating, args.ks)
    else:
        r, auc = ranklist_by_sorted(user_pos_test, test_items, rating, args.ks)

    # # .......checking.......
    # try:
    #     assert len(user_pos_test) != 0
    # except Exception:
    #     print(u)
    #     print(training_items)
    #     print(user_pos_test)
    #     exit()
    # # .......checking.......

    return get_performance(user_pos_test, r, auc, args.ks)


def test(sess, model, users_to_test, data_generator, args, drop_flag=False, batch_test_flag=False):
    result = {'precision': np.zeros(len(args.ks)), 'recall': np.zeros(len(args.ks)), 'ndcg': np.zeros(len(args.ks)),
              'hit_ratio': np.zeros(len(args.ks)), 'auc': 0.}
    
    pool = multiprocess.Pool(cores)

    if args.model_type in ['ripple']:

        u_batch_size = args.batch_size
        i_batch_size = args.batch_size // 20
    elif args.model_type in ['fm', 'nfm']:
        u_batch_size = args.batch_size
        i_batch_size = args.batch_size
    else:
        u_batch_size = args.batch_size * 2
        i_batch_size = args.batch_size

    test_users = users_to_test
    n_test_users = len(test_users)
    n_user_batchs = n_test_users // u_batch_size + 1

    count = 0

    for u_batch_id in range(n_user_batchs):
        start = u_batch_id * u_batch_size
        end = (u_batch_id + 1) * u_batch_size

        user_batch = test_users[start: end]

        if batch_test_flag:

            n_item_batchs = data_generator.n_items // i_batch_size + 1
            rate_batch = np.zeros(shape=(len(user_batch), data_generator.n_items))

            i_count = 0
            for i_batch_id in range(n_item_batchs):
                i_start = i_batch_id * i_batch_size
                i_end = min((i_batch_id + 1) * i_batch_size, data_generator.n_items)

                item_batch = range(i_start, i_end)

                feed_dict = data_generator.generate_test_feed_dict(model=model,
                                                                   user_batch=user_batch,
                                                                   item_batch=item_batch,
                                                                   drop_flag=drop_flag)
                i_rate_batch = model.eval(sess, feed_dict=feed_dict)
                i_rate_batch = i_rate_batch.reshape((-1, len(item_batch)))

                rate_batch[:, i_start: i_end] = i_rate_batch
                i_count += i_rate_batch.shape[1]

            assert i_count == data_generator.n_items

        else:
            item_batch = range(data_generator.n_items)
            feed_dict = data_generator.generate_test_feed_dict(model=model,
                                                               user_batch=user_batch,
                                                               item_batch=item_batch,
                                                               drop_flag=drop_flag)
            rate_batch = model.eval(sess, feed_dict=feed_dict)
            rate_batch = rate_batch.reshape((-1, len(item_batch)))

        user_batch_rating_uid = zip(rate_batch, user_batch)
        full_wrap = [(user_wrap, data_generator, args) for user_wrap in user_batch_rating_uid]
        batch_result = pool.map(test_one_user, full_wrap)
        count += len(batch_result)

        for re in batch_result:
            result['precision'] += re['precision']/n_test_users
            result['recall'] += re['recall']/n_test_users
            result['ndcg'] += re['ndcg']/n_test_users
            result['hit_ratio'] += re['hit_ratio']/n_test_users
            result['auc'] += re['auc']/n_test_users


    assert count == n_test_users
    pool.close()
    return result

def test_one_user_rank_list(x):
    user_wrap, data_generator, args = x
    # user u's ratings for user u and uid
    rating, u = user_wrap
    print(f"testing user {u}", end="; ", flush=True)
    try:
        training_items = data_generator.train_user_dict[u]
    except Exception:
        training_items = []

    test_items = list(data_generator.all_items - set(training_items))

    r, auc = ranklist_by_heapq(test_items, rating, args.ks)

    return u, r, auc

def test_rank_list(sess, model, users_to_test, data_generator, args, drop_flag=False, batch_test_flag=False):
    
    pool = multiprocess.Pool(cores)

    if args.model_type in ['ripple']:

        u_batch_size = args.batch_size
        i_batch_size = args.batch_size // 20
    elif args.model_type in ['fm', 'nfm']:
        u_batch_size = args.batch_size
        i_batch_size = args.batch_size
    else:
        u_batch_size = args.batch_size * 2
        i_batch_size = args.batch_size

    test_users = users_to_test
    n_test_users = len(test_users)
    n_user_batchs = n_test_users // u_batch_size + 1

    count = 0

    for u_batch_id in range(n_user_batchs):
        start = u_batch_id * u_batch_size
        end = (u_batch_id + 1) * u_batch_size

        user_batch = test_users[start: end]

        if batch_test_flag:

            n_item_batchs = data_generator.n_items // i_batch_size + 1
            rate_batch = np.zeros(shape=(len(user_batch), data_generator.n_items))

            i_count = 0
            for i_batch_id in range(n_item_batchs):
                i_start = i_batch_id * i_batch_size
                i_end = min((i_batch_id + 1) * i_batch_size, data_generator.n_items)

                item_batch = range(i_start, i_end)

                feed_dict = data_generator.generate_test_feed_dict(model=model,
                                                                   user_batch=user_batch,
                                                                   item_batch=item_batch,
                                                                   drop_flag=drop_flag)
                i_rate_batch = model.eval(sess, feed_dict=feed_dict)
                i_rate_batch = i_rate_batch.reshape((-1, len(item_batch)))

                rate_batch[:, i_start: i_end] = i_rate_batch
                i_count += i_rate_batch.shape[1]

            assert i_count == data_generator.n_items

        else:
            item_batch = range(data_generator.n_items)
            feed_dict = data_generator.generate_test_feed_dict(model=model,
                                                               user_batch=user_batch,
                                                               item_batch=item_batch,
                                                               drop_flag=drop_flag)
            rate_batch = model.eval(sess, feed_dict=feed_dict)
            rate_batch = rate_batch.reshape((-1, len(item_batch)))

        user_batch_rating_uid = zip(rate_batch, user_batch)
        full_wrap = [(user_wrap, data_generator, args) for user_wrap in user_batch_rating_uid]
        batch_result = pool.map(test_one_user_rank_list, full_wrap)
        count += len(batch_result)


    assert count == n_test_users
    pool.close()
    return batch_result