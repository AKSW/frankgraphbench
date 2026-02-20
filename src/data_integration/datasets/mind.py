import os

from ..dataset import Dataset

import pandas as pd

class MIND(Dataset):
    """
    General MIND class for all MIND datasets.
    """
    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers=n_workers)
        self.item_fields = [
            "item_id::string",
            "category::string",
            "subcategory::string",
            "title::string",
            "abstract::string",
            "url::string",
            "title_entities",
            "abstract_entities"
        ]
        self.user_fields = {"user_id":"user_id::string"}
        self.behavior_separator = " "  # separator for history and impressions in behavior file
        self.rating_fields = [
            "user_id::string",
            "item_id::string",
            "rating::number",
            "timestamp::string"
        ]
        self.map_fields = {
            "item_id": "item_id::string",
            "URI": "entities::string",
        }
        self.enrich_fields = [
            "item_id::string",
            "label::string",
            "type::string",
            "wikidata_id::string",
            "confidence::number",
        ]

class MINDSmall(MIND):
    """
    MIND Small dataset.
    """
    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers=n_workers)

    def load_item_data(self):
        # Reading item file of mind-small dataset
        filename = os.path.join(self.input_path, "news.tsv")
        df = pd.read_csv(filename, sep='\t', names=self.item_fields)
        
        del df["title_entities"]
        del df["abstract_entities"]
        
        return df
    
    def load_user_data(self):
        # Reading unique users out of behavior file of mind-small dataset
        filename = os.path.join(self.input_path, "behaviors.tsv")
        df = pd.read_csv(filename, sep='\t', names=["impression_id", "user_id", "time", "history", "impressions"])
        df = df[["user_id"]].drop_duplicates()
        return df.rename(columns=self.user_fields)
    
    def load_rating_data(self):
        # Reading and parsing behavior file of mind-small dataset
        filename = os.path.join(self.input_path, "behaviors.tsv")
        df = pd.read_csv(filename, sep='\t', names=["impression_id", "user_id", "time", "history", "impressions"])
        del df["history"]

        rating_df = {field: [] for field in self.rating_fields}
        for _, row in df.iterrows():
            for impression in row["impressions"].split(self.behavior_separator):
                item_id, rating = impression.split("-")
                rating_df["user_id::string"].append(row["user_id"])
                rating_df["item_id::string"].append(item_id)
                rating_df["rating::number"].append(int(rating))
                rating_df["timestamp::string"].append(row["time"])

        return pd.DataFrame(rating_df)
    
    def entity_linking(self, df_item):
        # adding maping info from the abstract and title entities
        filename = os.path.join(self.input_path, "news.tsv")
        df = pd.read_csv(filename, sep='\t', names=self.item_fields)

        if not set(df["item_id::string"].unique()).issubset(set(df_item["item_id"].unique())):
            raise ValueError("News tsv file contains news items that are not present in the item dataframe.")

        title_entities = df[["item_id::string", "title_entities"]][(df["title_entities"] != "[]") & (df["title_entities"].notna())]
        title_entities = title_entities.rename(columns={"item_id::string": "item_id::string", "title_entities": "entities::string"})

        abstract_entities = df[["item_id::string", "abstract_entities"]][(df["abstract_entities"] != "[]") & (df["abstract_entities"].notna())]
        abstract_entities = abstract_entities.rename(columns={"item_id::string": "item_id::string", "abstract_entities": "entities::string"})

        entities_mapping = pd.concat([title_entities, abstract_entities], ignore_index=True).drop_duplicates(subset=['item_id::string', 'entities::string']).reset_index(drop=True)

        return entities_mapping

    def enrich(self, df_map):
        # enrichment is done by adding the mapping info from the abstract and title entities
        enrich = {field: [] for field in self.enrich_fields}

        for _, row in df_map.iterrows():
            entities = eval(row["entities::string"])
            for entity in entities:
                enrich["item_id::string"].append(row["item_id::string"])
                enrich["label::string"].append(entity.get("Label", ""))
                enrich["type::string"].append(entity.get("Type", ""))
                enrich["wikidata_id::string"].append(entity.get("WikidataId", ""))
                enrich["confidence::number"].append(entity.get("Confidence", 0))

        return pd.DataFrame(enrich).set_index(self.enrich_fields[0])