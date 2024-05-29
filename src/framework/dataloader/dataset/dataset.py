class Dataset():
    def __init__(self):
        self.G_train = None
        self.ratings_train = None # {user: [(item1, rating), ... } Unordered items
        self.ratings_test = None
        self.has_val = False
        self.ratings_val = None
    
    def set_train_data(self, G, ratings):
        self.G_train = G
        self._sort_ratings(ratings)
        self.ratings_train = ratings
    
    def set_test_data(self, ratings):
        self._sort_ratings(ratings)
        self.ratings_test = ratings

    def set_val_data(self, ratings):
        self.has_val = True
        self._sort_ratings(ratings)
        self.ratings_val = ratings

    def get_train_data(self):
        return self.G_train, self.ratings_train

    def get_test_data(self):
        return self.ratings_test

    def get_val_data(self):
        return self.ratings_val
    
    def has_val_data(self):
        return self.has_val
    
    def _sort_ratings(self, ratings):
        # inplace sorting
        for u in ratings.keys():
            ratings[u].sort(reverse=True, key=lambda x: x[1])