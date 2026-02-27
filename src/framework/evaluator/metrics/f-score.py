from ..metric import Metric 
from .precision import Precision
from .recall import Recall

class FScore(Metric):
    def __init__(self, k: int, relevance_threshold: int = 0, beta: float = 1.0):
        super().__init__(k, relevance_threshold)
        self.beta = beta
    
    def name(self):
        return f'F{self.beta}-score@{self.k}'
    
    def eval(self, ratings, recommendations):
        precision_metric = Precision(self.k, self.relevance_threshold)
        recall_metric = Recall(self.k, self.relevance_threshold)
        
        precision = precision_metric.eval(ratings, recommendations)
        recall = recall_metric.eval(ratings, recommendations)
        
        if precision + recall == 0:
            return 0.0
        
        beta_squared = self.beta ** 2
        f_score = (1 + beta_squared) * (precision * recall) / (beta_squared * precision + recall)
        
        return f_score