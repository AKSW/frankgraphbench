class Dataset():
    def __init__(self):
        self.G_train = None
        self.ratings_train = None
        self.labels_train = None
        self.ratings_test = None
        self.labels_test = None
        self.ratings_val = None
        self.labels_val = None
    
    def set_train_data(self, G, X, y):
        self.G_train = G
        self.ratings_train = X
        self.labels_train = y
    
    def set_test_data(self, X, y):
        self.ratings_test = X
        self.labels_test = y

    def set_val_data(self, X, y):
        self.ratings_val = X
        self.labels_val = y

    def get_train_data(self):
        return self.G_train, self.ratings_train, self.labels_train

    def get_test_data(self):
        return self.ratings_test, self.labels_test

    def get_val_data(self):
        return self.ratings_val, self.labels_val
