import os
import re
import queue
from string import Template
from .dataset import Dataset
from .worker import Worker

import pandas as pd
from tqdm import tqdm
from thefuzz import process

class BookCrossing(Dataset):
    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers)
        self.dataset_name = 'Book-Crossing'

        self.item_separator = ';'
        self.user_separator = ';'
        self.rating_separator = ';'

        self.item_fields = ['item_id', 'title', 'author', 'year', 'publisher']
        # self.user_fields = ['user_id', 'age', 'gender', 'occupation']
        self.rating_fields = ['user_id', 'item_id', 'rating']
        # self.map_fields = ['item_id', 'URI']


    def load_item_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, 'BX-Books.csv')

        df = pd.read_csv(filename, sep=self.item_separator, encoding='CP1252', escapechar='\\')
        df = df.drop(df.columns[-3:], axis=1) # Will not use picture URL related fields
        df.columns = self.item_fields
        return df

   