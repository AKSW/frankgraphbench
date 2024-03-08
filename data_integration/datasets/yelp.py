import json
import pandas as pd
from tqdm import tqdm

from ..dataset import Dataset

class Yelp(Dataset):
    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers)
        self.dataset_name = "Yelp"

        self.categories_separator = ", "
        self.friends_separator = ", "

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
            "hours": "hours::string_list"
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