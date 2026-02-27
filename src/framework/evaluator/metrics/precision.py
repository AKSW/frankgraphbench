from ..metric import Metric

class Precision(Metric):
    def __init__(self, k: int, relevance_threshold: int = 0):
        super().__init__(k, relevance_threshold)
    
    def name(self):
        return f'Precision@{self.k}'
    
    def eval(self, ratings, recommendations):
        relevant_items = self._get_relevant_ratings(ratings)
        users_precision = [self._precision(set(rel_items), recommendations[u]) for u, rel_items in relevant_items.items()]
        return sum(users_precision) / len(users_precision) if users_precision else 0.0
    
    def _precision(self, rel_items, recommendations):
        if len(recommendations) > self.k:
            recommendations = recommendations[:self.k]
        
        if not recommendations:
            return 0.0
        
        num_relevant_and_recommended = sum(1 for rec in recommendations if rec in rel_items)
        return num_relevant_and_recommended / len(recommendations) if recommendations else 0.0