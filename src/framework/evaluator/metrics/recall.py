from ..metric import Metric

class Recall(Metric):
    def __init__(self, k: int, relevance_threshold: int = 0):
        super().__init__(k, relevance_threshold)
    
    def name(self):
        return f'Recall@{self.k}'
    
    def eval(self, ratings, recommendations):
        relevant_items = self._get_relevant_ratings(ratings)
        users_recall = [self._recall(set(rel_items), recommendations[u]) for u, rel_items in relevant_items.items()]
        return sum(users_recall) / len(users_recall) if users_recall else 0.0
    
    def _recall(self, rel_items, recommendations):
        if len(recommendations) > self.k:
            recommendations = recommendations[:self.k]
        
        if not rel_items:
            return 0.0
        
        num_relevant_and_recommended = sum(1 for rec in recommendations if rec in rel_items)
        return num_relevant_and_recommended / len(rel_items) if rel_items else 0.0