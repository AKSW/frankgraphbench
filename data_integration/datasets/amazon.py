import os
import gzip
import json
import pandas as pd
import re
from collections import defaultdict
from bs4 import BeautifulSoup

from ..dataset import Dataset

class Amazon(Dataset):
    """
    General Amazon(Dataset) class for data loading all different Amazon datasets
    """
    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers)
    
    def _parse(self, path):
        g = gzip.open(path, 'rb')
        for l in g:
            yield json.loads(l)

    def _getDF(self, path):
        i = 0
        df = {}
        for d in self._parse(path):
            df[i] = d
            i += 1
        return pd.DataFrame.from_dict(df, orient='index')
    
class AmazonVideoGames5(Amazon):
    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers)
        self.dataset_name = "Amazon Video Games 5-core"

        self.string_list_separator = "::"

        self.item_fields = {
            "asin": "item_id::string",
            "title": "name::string",
            "feature": "features::string_list",
            "description": "description::string",
            "price": "price::number",
            "also_buy": "also_buy::string_list",
            "also_view": "also_view::string_list",
            "brand": "brand::string",
            "category": "categories::string_list"
        }

        self.user_fields = {
            "reviewerID": "user_id::string",
            "reviewerName": "name::string",
        }

        self.rating_fields = {
            "reviewerID": "user_id::string",
            "asin": "item_id::string",
            "reviewText": "text::string",
            "overall": "rating::number",
            "summary": "summary::string",
            "unixReviewTime": "timestamp::number"
        }

    def load_item_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "Video_Games_5.json.gz")
        print(filename)
        df = self._getDF(filename)

        filename = os.path.join(self.input_path, "meta_Video_Games.json.gz")
        print(filename)
        meta_df = self._getDF(filename)
        meta_df = meta_df[meta_df['asin'].isin(df['asin'].unique())].reset_index(drop=True)

        features = defaultdict(list)
        for index, row in meta_df['feature'].dropna().items():
            for feature in row:
                soup = BeautifulSoup(feature, 'html.parser')
                feature = soup.text
                if "" != feature:
                    features[index].append(feature)
        meta_df['feature'] = pd.Series(features).apply(lambda x: self.string_list_separator.join(x))
        
        descriptions = defaultdict(list)
        for index, row in meta_df['description'].dropna().items():
            for description in row:
                soup = BeautifulSoup(description, 'html.parser')
                description = soup.text
                if "" != description:
                    descriptions[index].append(description)
        meta_df['description'] = pd.Series(descriptions).apply(lambda x: " ".join(x))

        numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
        rx = re.compile(numeric_const_pattern, re.VERBOSE)
        meta_df['price'] = meta_df['price'].apply(lambda x: rx.findall(x))
        meta_df['price'] = meta_df['price'].apply(lambda x: x[0] if len(x) > 0 else None)
        meta_df['price'] = meta_df['price'].astype('float64')

        also_buys = defaultdict(list)
        for index, row in meta_df['also_buy'].dropna().items():
            for also_buy in row:
                also_buys[index].append(also_buy)
        meta_df['also_buy'] = pd.Series(also_buys).apply(lambda x: self.string_list_separator.join(x))

        also_views = defaultdict(list)
        for index, row in meta_df['also_view'].dropna().items():
            for also_view in row:
                also_views[index].append(also_view)
        meta_df['also_view'] = pd.Series(also_views).apply(lambda x: self.string_list_separator.join(x))

        categories = defaultdict(list)
        for index, row in meta_df['category'].dropna().items():
            for category in row:
                soup = BeautifulSoup(category, 'html.parser')
                category = soup.text
                if "" != category:
                    categories[index].append(category)
        meta_df['category'] = pd.Series(categories).apply(lambda x: self.string_list_separator.join(x))

        meta_df = meta_df.rename(self.item_fields, axis=1)
        meta_df = meta_df[self.item_fields.values()]
        return meta_df
    
    def load_user_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "Video_Games_5.json.gz")
        print(filename)
        df = self._getDF(filename)

        df = df.rename(self.user_fields, axis=1)
        df = df[self.user_fields.values()]
        return df
    
    def load_rating_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "Video_Games_5.json.gz")
        print(filename)
        df = self._getDF(filename)

        df = df.rename(self.rating_fields, axis=1)
        df = df[self.rating_fields.values()]
        return df

