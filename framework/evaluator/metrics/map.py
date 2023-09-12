from ..metric import Metric

import numpy as np

class MAP(Metric):
    # reference: https://github.com/benhamner/Metrics/blob/master/Python/ml_metrics/average_precision.py
    def init(self, k : int, relevance_threshold=0):
        super().init(k, relevance_threshold)

    def name(self):
        return 'MAP'
    
    def eval(self, ratings, recommendations):
        relevant_items = self._get_relevant_ratings(ratings)
        users_apk = [self._apk(set(rel_items), recommendations[u]) for u, rel_items in relevant_items.items()]
        return np.mean(users_apk)
    
    def _apk(self, rel_items, recommendations):
        if len(recommendations) > self.k:
            recommendations = recommendations[:self.k]
        
        score = 0.0
        num_hits = 0.0

        if not rel_items:
            return score

        for i, rec in enumerate(recommendations):
            if rec in rel_items and rec not in recommendations[:i]:
                num_hits += 1.0
                score += num_hits/(i+1.0)

        return score/min(len(rel_items), self.k)