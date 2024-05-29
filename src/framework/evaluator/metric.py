class Metric:
    def __init__(self, k : int, relevance_threshold : int = 0):
        self.k = k
        self.relevance_threshold = relevance_threshold

    def name(self) -> str:
        raise NotImplementedError('Implement the name() method for your metric subclass')

    def eval(self, ratings, recommendations):
        """
        Evaluate recommendation metric over user ratings
        :param ratings: ratings used as ground truth
            of type {user: [(item1, rating1), (item2, rating2), ...]}
        :param recommendations: model k first recommendations
            of type {user: [(item1, rating1), (item2, rating2), ...]}
        """
        raise NotImplementedError('Implement the eval() method for your metric subclass')
    
    def _get_relevant_ratings(self, ratings, with_ratings=False):
        relevant_ratings = {}
        for u, u_ratings in ratings.items():
            relevant_items = []
            for (i, rating) in u_ratings:
                if rating >= self.relevance_threshold:
                    if not with_ratings:
                        relevant_items.append(i)
                    else:
                        relevant_items.append((i, rating))
                else:
                    # It's sorted, so I'm sure the next ones wont be greater than threshold
                    break
            
            if len(relevant_items) > 0:
                relevant_ratings[u] = relevant_items
        
        return relevant_ratings
            
            
                