import os
import json
import pandas as pd
from collections import defaultdict

from ..dataset import Dataset

class Yelp(Dataset):
    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers)
        self.dataset_name = "Yelp"

        self.categories_separator = ", "
        self.friends_separator = ", "
        self.elites_separator = ","

        self.string_list_separator = "::"

        self.item_fields = {
            "business_id": "item_id::string",
            "name": "name::string",
            "address": "address::string",
            "city": "city::string",
            "state": "state::string",
            "postal_code": "postal_code::string",
            "latitude": "latitute::number",
            "longitude": "longitude::number",
            "stars": "stars::number",
            "review_count": "review_count::number",
            "is_open": "is_open::number",
            "attributes": "attributes::string_list",
            "categories": "categories::string_list",
        }

        self.user_fields = {
            "user_id": "user_id::string",
            "name": "name::string",
            "review_count": "review_count::number",
            "yelping_since": "yelping_since::string",
            "useful": "useful_count::number",
            "funny": "funny_count::number",
            "cool": "cool_count::number",
            "elite": "elite_years::string_list",
            "fans": "fans_count::number",
            "average_stars": "average_stars::number",
            "compliment_hot": "compliment_hot_count::number",
            "compliment_more": "compliment_more_count::number",
            "compliment_profile": "compliment_cute_count::number",
            "compliment_list": "compliment_list_count::number",
            "compliment_note": "compliment_note_count::number",
            "compliment_plain": "compliment_plain_count::number",
            "compliment_cool": "compliment_cool_count::number",
            "compliment_funny": "compliment_funny_count::number",
            "compliment_writer": "compliment_writer_count::number",
            "compliment_photos": "compliment_photos_count::number"
        }

        self.rating_fields = {
            "user_id": "user_id::string",
            "business_id": "item_id::string",
            "stars": "rating::number",
            "useful": "useful_count::number",
            "funny": "funny_count::number",
            "cool": "cool_count::number",
            "text": "text::string",
            "date": "date::string"
        }

        self.social_fields = {"user_id": "user1::string", "friend_id": "user2::string"}

    def load_item_data(self) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "yelp_academic_dataset_business.json")

        print(filename)
        file = open(filename)
        data = []
        for line in file:
            data.append(json.loads(line))
        df = pd.DataFrame(data)
        file.close()

        attributes = defaultdict(list)
        for index, row in df['attributes'].dropna().items():
            for key, value in row.items():
                if value == 'True':
                    attributes[index].append(key)
        df['attributes'] = pd.Series(attributes).apply(lambda x: self.string_list_separator.join(x))

        categories = defaultdict(list)
        for index, row in df['categories'].dropna().items():
            for category in row.split(self.categories_separator):
                categories[index].append(category)
        pd.Series(categories).apply(lambda x: self.string_list_separator.join(x))

        df = df.rename(self.item_fields, axis=1)
        df = df[self.item_fields.values()]
        return df
    
    def load_user_data(self) -> pd.DataFrame:
        filename = os.path.join(self.input_path, "yelp_academic_dataset_user.json")

        file = open(filename)
        data = []
        for line in file:
            data.append(json.loads(line))
        df = pd.DataFrame(data)
        file.close()

        elites = defaultdict(list)
        for index, row in df['elite'].dropna().items():
            for elite in row.split(self.elites_separator):
                elites[index].append(elite)
        pd.Series(elites).apply(lambda x: self.string_list_separator.join(x))

        df = df.rename(self.user_fields, axis=1)
        df = df[self.user_fields.values()]
        return df
    
    def load_rating_data(self) -> pd.DataFrame:
        filename = os.path.join(self.input_path, "yelp_academic_dataset_review.json")

        file = open(filename)
        data = []
        for line in file:
            data.append(json.loads(line))
        df = pd.DataFrame(data)
        file.close()
        df = df.rename(self.rating_fields, axis=1)
        df = df[self.rating_fields.values()]
        return df
    
    def load_social_data(self) -> pd.DataFrame:
        filename = os.path.join(self.input_path, "yelp_academic_dataset_user.json")

        file = open(filename)
        data = []
        for line in file:
            data.append(json.loads(line))
        user_df = pd.DataFrame(data)
        file.close()

        friends = defaultdict(list)
        for index, row in user_df['friends'].dropna().items():
            for friend in row.split(self.friends_separator):
                friends[index].append(friend)

        social = {'user_id': [], 'friend_id': []}
        for index, friends_list in friends.items():
            for friend in friends_list:
                social["user_id"].append(user_df['user_id'].iloc[index])
                social["friend_id"].append(friend)
        pd.DataFrame(social)
        
        df = pd.DataFrame(social)
        df = df.rename(self.social_fields, axis=1)
        df = df[self.social_fields.values()]
        return df
