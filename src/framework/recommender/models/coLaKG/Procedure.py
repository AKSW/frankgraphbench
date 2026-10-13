
import multiprocessing

import numpy as np
import torch

from framework.recommender.models.coLaKG import colakg_utils
from framework.recommender.models.coLaKG.colakg_utils import timer

CORES = multiprocessing.cpu_count() // 2


def BPR_train_original(dataset, recommend_model, loss_class, epoch, neg_k=1, w=None, batch_size=32):
    Recmodel = recommend_model
    Recmodel.train()
    bpr: colakg_utils.BPRLoss = loss_class

    with timer(name="Sample"):
       S = colakg_utils.UniformSample_original(dataset)
    users = torch.Tensor(S[:, 0]).long()
    posItems = torch.Tensor(S[:, 1]).long()
    negItems = torch.Tensor(S[:, 2]).long()

    users, posItems, negItems = colakg_utils.shuffle(users, posItems, negItems)
    total_batch = len(users) // batch_size
    aver_loss = 0.
    for (batch_i,
         (batch_users,
         batch_pos,
         batch_neg)) in enumerate(colakg_utils.minibatch(users,
                                                  posItems,
                                                  negItems,
                                                  batch_size=batch_size)):
       cri = bpr.stageOne(batch_users, batch_pos, batch_neg)
       aver_loss += cri

    aver_loss = aver_loss / total_batch
    time_info = timer.dict()
    timer.zero()
    return f"loss{aver_loss:.3f}-{time_info}"
    
    
def test_one_batch(X, topks):
    sorted_items = X[0].numpy()
    groundTrue = X[1]
    r = colakg_utils.getLabel(groundTrue, sorted_items)
    pre, recall, ndcg = [], [], []
    for k in topks:
      ret = colakg_utils.RecallPrecision_ATk(groundTrue, r, k)
      pre.append(ret['precision'])
      recall.append(ret['recall'])
      ndcg.append(colakg_utils.NDCGatK_r(groundTrue, r, k))
    return {'recall': np.array(recall),
            'precision': np.array(pre),
            'ndcg': np.array(ndcg)}
        
            
def Test(dataset, Recmodel, epoch, w=None, multicore=0, topks=(1, 10, 100), u_batch_size=32):
    dataset: colakg_utils.BasicDataset
    testDict: dict = dataset.testDict
      # eval mode with no dropout
    Recmodel = Recmodel.eval()
    topks = list(topks)
    max_K = max(topks)
    pool = multiprocessing.Pool(CORES) if multicore == 1 else None
    results = {'precision': np.zeros(len(topks)),
              'recall': np.zeros(len(topks)),
              'ndcg': np.zeros(len(topks))}
    with torch.no_grad():
       users = list(testDict.keys())
       try:
           assert u_batch_size <= len(users) / 10
       except AssertionError:
           print(f"test_u_batch_size is too big for this dataset, try a small one {len(users) // 10}")
       users_list = []
       rating_list = []
       groundTrue_list = []
       total_batch = len(users) // u_batch_size + 1
       for batch_users in colakg_utils.minibatch(users, batch_size=u_batch_size):
           allPos = dataset.getUserPosItems(batch_users)
           groundTrue = [testDict[u] for u in batch_users]
           batch_users = torch.Tensor(batch_users).long()

           rating = Recmodel.getUsersRating(batch_users)
           exclude_index = []
           exclude_items = []
           for range_i, items in enumerate(allPos):
               exclude_index.extend([range_i] * len(items))
               exclude_items.extend(items)
           rating[exclude_index, exclude_items] = -(1 << 10)
           _, rating_K = torch.topk(rating, k=max_K)
           del rating
           rating_list.append(rating_K.cpu())
           groundTrue_list.append(groundTrue)

       assert len(rating_list) == total_batch
       X = zip(rating_list, groundTrue_list)
       if multicore == 1:
           pre_results = [test_one_batch(x, topks) for x in X]
       else:
           pre_results = [test_one_batch(x, topks) for x in X]
       for result in pre_results:
           results['recall'] += result['recall']
           results['precision'] += result['precision']
           results['ndcg'] += result['ndcg']
       results['recall'] /= float(len(users))
       results['precision'] /= float(len(users))
       results['ndcg'] /= float(len(users))
       print(results)
       return results
