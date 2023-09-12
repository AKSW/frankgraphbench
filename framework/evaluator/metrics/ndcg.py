from ..metric import Metric
import numpy as np

class nDCG(Metric):
    def __init__(self, k: int, relevance_threshold: int = 0):
        super().__init__(k, relevance_threshold)
    
    def name(self):
        return 'nDCG'
    
    def eval(self, ratings, recommendations):
        relevant_items = self._get_relevant_ratings(ratings, with_ratings=True)
        users_ndcg = []
        for u, rel_items in relevant_items.items():
            u_recs = self._get_user_rec_relevance(rel_items, recommendations[u])
            ndcg = self._calculate_ndcg(rel_items, u_recs)
            users_ndcg.append(ndcg)
        
        return np.mean(users_ndcg)

    def _calculate_dcg(self, recs):
        recs = np.asfarray(recs)[:self.k]
        if not recs.size:
            return 0.0
        else:
            return np.sum(recs / np.log2(np.arange(2, recs.size+2)))
        
    def _get_user_rec_relevance(self, relevant_items, recs):
        rel = {} # {item: float(rating)}
        for (item, rating) in relevant_items:
            rel[item] = rating
        
        recs_relevance = []
        for item in recs:
            item_rel = float(rel.get(item, 0.0))
            recs_relevance.append(item_rel)
        
        return recs_relevance

        
    def _calculate_ndcg(self, relevant_items, recs):
        # already ordered
        relevant_items = [rating for _, rating in relevant_items[:self.k]]
        idcg = self._calculate_dcg(relevant_items)
        if not idcg:
            return 0.0
        else:
            return self._calculate_dcg(recs) / idcg
    