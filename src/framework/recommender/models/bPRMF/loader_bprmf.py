'''
Created on Dec 18, 2018
Tensorflow Implementation of the Baseline Model, BPRMF, in:
Wang Xiang et al. KGAT: Knowledge Graph Attention Network for Recommendation. In KDD 2019.
@author: Xiang Wang (xiangwang@u.nus.edu)
@modifiedBy: Paulo do Carmo on Dec, 2025
'''
from framework.recommender.utils.load_data import Data


class BPRMF_loader(Data):
    def __init__(self, ratings_triples, item_property_triples, args, batch_size, random_seed):
        super().__init__(ratings_triples, item_property_triples, args, batch_size, random_seed)

    def generate_train_batch(self):
        users, pos_items, neg_items = self._generate_train_cf_batch()

        batch_data = {}
        batch_data['users'] = users
        batch_data['pos_items'] = pos_items
        batch_data['neg_items'] = neg_items

        return batch_data

    def generate_train_feed_dict(self, model, batch_data):
        # PyTorch version: hand the numpy batch straight through to the model.
        return batch_data


    def generate_test_feed_dict(self, model, user_batch, item_batch):
        feed_dict = {
            'users': user_batch,
            'items': item_batch
        }
        return feed_dict

