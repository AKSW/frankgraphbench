from typing import Dict, List, Tuple
from framework.dataloader.graph.graph import Graph
from framework.dataloader.graph.node import ItemNode, UserNode
from framework.recommender.models.kGAT.helper import early_stopping
from framework.recommender.models.kGAT.batch_test import test, test_rank_list
from framework.recommender.models.kGAT.loader_kgat import KGAT_loader
from framework.recommender.models.kGAT.KGAT import KGAT_model

from ...recommender import Recommender

import numpy as np
import tensorflow as tf
from time import time

import argparse
import sys

class KGAT(Recommender):
    def __init__(
                    self, 
                    config : dict,
                    model_type: str = 'kgat',
                    verbose: int = 50,
                    embed_size: int = 64,
                    epoch: int = 1000,
                    validate_factor: int = 10,
                    validate_frac: float = 0.1,
                    kge_size: int = 64,
                    layer_size: list = [64,32,16],
                    batch_size: int = 1024,
                    batch_size_kg: int = 2048,
                    test_flag: str = 'part',
                    regs: list = [1e-5,1e-5,1e-2],
                    node_dropout: list = [0.1],
                    mess_dropout: list = [0.1,0.1,0.1],
                    lr: float = 0.0001,
                    adj_type: str = 'si',
                    adj_uni_type: str = 'sum',
                    alg_type: str = 'bi',
                    use_att: bool = True,
                    use_kge: bool = True,
                    report: int = 0,
                    ks: list = [10],
                 ):
        super().__init__(config)
        args_dict = {
            'model_type': model_type,
            'verbose': verbose,
            'epoch': epoch,
            'validate_factor': validate_factor,
            'validate_frac': validate_frac,
            'embed_size': embed_size,
            'kge_size': kge_size,
            'layer_size': layer_size,
            'batch_size': batch_size,
            'batch_size_kg': batch_size_kg,
            'test_flag': test_flag,
            'regs': regs,
            'node_dropout': node_dropout,
            'mess_dropout': mess_dropout,
            'lr': lr,
            'adj_uni_type': adj_uni_type,
            'alg_type': alg_type,
            'adj_type': adj_type,
            'use_att': use_att,
            'use_kge': use_kge,
            'report': report,
            'ks': ks
        }
        self._args = argparse.Namespace(**args_dict)

        self.n_layers = len(layer_size)
        self.adj_type = adj_type
        self.adj_uni_type = adj_uni_type
        self.alg_type = alg_type

    def name(self):
        text = "KGAT"
        text += f";n_layers={self.n_layers};adj_type={self.adj_type};adj_uni_type={self.adj_uni_type};alg_type{self.alg_type}"
        return text
    
    def train(self, G_train: Graph, ratings_train: Dict[UserNode, List[Tuple[ItemNode, float]]]):
        self.ratings_train = ratings_train
        self.G_train = G_train.convert_node_labels_to_integer()
        self._ratings_triples = self.G_train.get_ratings_triples(return_type="int")
        self._item_property_triples = self.G_train.get_item_property_triples(return_type="int")
        
        self._data_generator = KGAT_loader(ratings_triples=self._ratings_triples, item_property_triples=self._item_property_triples, args=self._args)
        
        self._config = dict()
        self._config['n_users'] = self._data_generator.n_users
        self._config['n_items'] = self._data_generator.n_items
        self._config['n_relations'] = self._data_generator.n_relations
        self._config['n_entities'] = self._data_generator.n_entities

        # "Load the laplacian matrix."
        self._config['A_in'] = sum(self._data_generator.lap_list)

        # "Load the KG triplets."
        self._config['all_h_list'] = self._data_generator.all_h_list
        self._config['all_r_list'] = self._data_generator.all_r_list
        self._config['all_t_list'] = self._data_generator.all_t_list
        self._config['all_v_list'] = self._data_generator.all_v_list

        t0 = time()

        self._pretrain_data = None

        self._model = KGAT_model(data_config=self._config, pretrain_data=self._pretrain_data, args=self._args)
        
        self.fit(t0)

    def fit(self, t0):
        config = tf.compat.v1.ConfigProto()
        config.gpu_options.allow_growth = True
        self._sess = tf.compat.v1.Session(config=config)

        self._sess.run(tf.compat.v1.global_variables_initializer())
        cur_best_pre_0 = 0.

        loss_loger, pre_loger, rec_loger, ndcg_loger, hit_loger = [], [], [], [], []
        stopping_step = 0
        should_stop = False
        self._batch_test_flag = False

        # train
        for epoch in range(self._args.epoch):
            t1 = time()
            loss, base_loss, kge_loss, reg_loss = 0., 0., 0., 0.
            n_batch = self._data_generator.n_train // self._args.batch_size + 1

            for _ in range(n_batch):
                batch_data = self._data_generator.generate_train_batch()
                feed_dict = self._data_generator.generate_train_feed_dict(self._model, batch_data)

                _, batch_loss, batch_base_loss, batch_kge_loss, batch_reg_loss = self._model.train(self._sess, feed_dict=feed_dict)

                loss += batch_loss
                base_loss += batch_base_loss
                kge_loss += batch_kge_loss
                reg_loss += batch_reg_loss

            if np.isnan(loss):
                print('ERROR: loss@phase1 is nan.')
                sys.exit()

            n_A_batch = len(self._data_generator.all_h_list) // self._args.batch_size_kg + 1

            if self._args.use_kge is True:
                # using KGE method
                for idx in range(n_A_batch):
                    A_batch_data = self._data_generator.generate_train_A_batch()
                    feed_dict = self._data_generator.generate_train_A_feed_dict(self._model, A_batch_data)

                    _, batch_loss, batch_kge_loss, batch_reg_loss = self._model.train_A(self._sess, feed_dict=feed_dict)

                    loss += batch_loss
                    kge_loss += batch_kge_loss
                    reg_loss += batch_reg_loss
            
            if self._args.use_att is True:
                # updating attentive laplacian matrix.
                self._model.update_attentive_A(self._sess)
            
            if np.isnan(loss):
                print('ERROR: loss@phase2 is nan.')
                sys.exit()

            if (epoch + 1) % self._args.validate_factor != 0:
                if self._args.verbose > 0 and epoch % self._args.verbose == 0:
                    perf_str = 'Epoch %d [%.1fs]: train==[%.5f=%.5f + %.5f + %.5f]' % (
                        epoch, time() - t1, loss, base_loss, kge_loss, reg_loss)
                    print(perf_str)
                continue

            # validate
            t2 = time()
            users_to_test = list(self._data_generator.test_user_dict.keys())
            ret = test(self._sess, self._model, users_to_test, self._data_generator, self._args, drop_flag=False, batch_test_flag=self._batch_test_flag)

            # performance logging
            t3 = time()

            loss_loger.append(loss)
            rec_loger.append(ret['recall'])
            pre_loger.append(ret['precision'])
            ndcg_loger.append(ret['ndcg'])
            hit_loger.append(ret['hit_ratio'])

            if self._args.verbose > 0:
                perf_str = 'Epoch %d [%.1fs + %.1fs]: train==[%.5f=%.5f + %.5f + %.5f], recall=[%.5f, %.5f], ' \
                    'precision=[%.5f, %.5f], hit=[%.5f, %.5f], ndcg=[%.5f, %.5f]' % \
                    (epoch, t2 - t1, t3 - t2, loss, base_loss, kge_loss, reg_loss, ret['recall'][0], ret['recall'][-1],
                        ret['precision'][0], ret['precision'][-1], ret['hit_ratio'][0], ret['hit_ratio'][-1],
                        ret['ndcg'][0], ret['ndcg'][-1])
                print(perf_str)

            cur_best_pre_0, stopping_step, should_stop = early_stopping(ret['recall'][0], cur_best_pre_0,
                                                        stopping_step, expected_order='acc', flag_step=10)
            
            if should_stop:
                break

        # testing print
        recs = np.array(rec_loger)
        pres = np.array(pre_loger)
        ndcgs = np.array(ndcg_loger)
        hit = np.array(hit_loger)

        best_rec_0 = max(recs[:, 0])
        idx = list(recs[:, 0]).index(best_rec_0)

        final_perf = "Best Iter=[%d]@[%.1f]\trecall=[%s], precision=[%s], hit=[%s], ndcg=[%s]" % \
                    (idx, time() - t0, '\t'.join(['%.5f' % r for r in recs[idx]]),
                    '\t'.join(['%.5f' % r for r in pres[idx]]),
                    '\t'.join(['%.5f' % r for r in hit[idx]]),
                    '\t'.join(['%.5f' % r for r in ndcgs[idx]]))
        print(final_perf)


    def get_recommendations(self, k : int = 5) -> Dict[UserNode, List[ItemNode]]:
        users_to_test = list(self._data_generator.train_user_dict.keys()) + list(self._data_generator.test_user_dict.keys())
        ret = test_rank_list(self._sess, self._model, users_to_test, self._data_generator, self._args, drop_flag=False, batch_test_flag=self._batch_test_flag)
        print(ret)
        raise NotImplementedError('Override get_recommendations() for your model subclass.')

    def get_user_recommendation(self, user : UserNode, k : int = 5):
        raise NotImplementedError('Override get_user_recommendation() for your model subclass.')