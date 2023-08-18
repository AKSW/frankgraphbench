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
        self.X = X
        self.y = y
    
    def set_test_data(self, X, y):
        self.ratings_test = X
        self.labels_test = y

    def set_val_data(self, X, y):
        self.ratings_val = X
        self.labels_val = y
