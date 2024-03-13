import os
import pandas as pd

from ..dataset import Dataset

class DoubanMovie(Dataset):
    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers)
        self.dataset_name = "Douban Movie Short"

        self.item_fields_extract = ["Movie_Name_EN", "Movie_Name_CN"]
        self.user_fields_extract = ["Username"]
        self.rating_fields_extract = ["ID", "Date", "Star", "Comment", "Like", "Movie_Name_EN", "Username"]

        self.item_fields = {
            "movie_id": "item_id::string",
            "Movie_Name_EN": "name_EN::string",
            "Movie_Name_CN": "name_CN::string"
        }

        self.user_fields = {
            "user_id": "user_id::string",
            "Username": "name::string"
        }

        self.rating_fields = {
            "user_id": "user_id::string",
            "movie_id": "item_id::string",
            "Star": "rating::number",
            "Date": "date::string",
            "Comment": "comment::string",
            "Like": "like_count::number"
        }

    def load_item_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "DMSC.csv")
        df = pd.read_csv(filename)
        
        df = df[self.item_fields_extract].drop_duplicates().reset_index(drop=True)
        df['movie_id'] = df.index

        df = df.rename(self.item_fields, axis=1)
        df = df[self.item_fields.values()]
        return df
    
    def load_user_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "DMSC.csv")
        df = pd.read_csv(filename)
        
        df = df[self.user_fields_extract].drop_duplicates().reset_index(drop=True)
        df['user_id'] = df.index

        df = df.rename(self.user_fields, axis=1)
        df = df[self.user_fields.values()]
        return df
    
    def load_rating_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "DMSC.csv")
        df = pd.read_csv(filename)

        item_df = df[self.item_fields_extract].drop_duplicates().reset_index(drop=True)
        item_df['movie_id'] = item_df.index

        user_df = df[self.user_fields_extract].drop_duplicates().reset_index(drop=True)
        user_df['user_id'] = user_df.index
        
        df = df[self.rating_fields_extract].drop_duplicates().reset_index(drop=True)
        
        df = df.join(item_df.set_index('Movie_Name_EN'), on='Movie_Name_EN')
        df = df.join(user_df.set_index('Username'), on='Username')

        df = df.rename(self.rating_fields, axis=1)
        df = df[self.rating_fields.values()]
        return df

