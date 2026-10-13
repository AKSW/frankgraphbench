import os
import queue
from collections import defaultdict
from io import BytesIO
from string import Template

import pandas as pd
import polars as pl
from pandas.errors import EmptyDataError
from tqdm import tqdm

from ..dataset import Dataset


class CHEMBL(Dataset):
    def __init__(self, input_path, output_path, n_workers=1, sparql_endpoint="http://141.57.8.18:8896/sparql"):
        super().__init__(input_path, output_path, n_workers, sparql_endpoint)
        self.dataset_name = "CHEMBL"

         # raw CSV is comma separated
        self.item_separator = ","
        self.user_separator = ","
        self.rating_separator = ","

         # Item (chemical compound) fields. Every column of mixed.csv except the
         # two target columns is kept; the standardized name keeps the original
         # ChEMBL column name and only appends the "::type" suffix, matching the
         # pattern used in dataset.py / lastfm.py.
        self.item_fields = {
              "Molecule ChEMBL ID": "molecule_chembl_id::string",
              "Molecular Weight": "molecular_weight::number",
              "#RO5 Violations": "number_ro5_violations::number",
              "AlogP": "alogp::number",
              "Standard Relation": "standard_relation::string",
              "Value(nM)": "value(nM)::number",
            #   "Activity": "Activity::string",
            #   "Unnamed: 0.2": "Unnamed: 0.2::number",
              "CID": "cid::number",
              "MolecularFormula": "molecular_formula::string",
              "SMILES": "smiles::string",
              "InChI": "inchi::string",
              "InChIKey": "inchi_key::string",
              "IUPACName": "iupac_name::string",
              "TPSA": "tpsa::number",
        }
        # User (biological target) fields. Only the target identifier is kept as
        # a user attribute; the sequential user_id is added in load_user_data().
        self.user_fields = {
            "Target ChEMBL ID": "target_chembl_id::string",
            "Target Type": "target_type::string",
        }

        # Rating (interaction) fields. A rating is the activity of a compound
        # (item) in a target (user), derived from the Activity column of
        # mixed.csv: ACTIVE -> 1, INACTIVE -> 0.
        self.rating_fields = {
            "user_id": "user_id::string",
            "item_id": "item_id::string",
            "rating": "rating::number",
        }

        self.map_fields = {
             "item_id": "item_id::string",
             "URI": "coco_id::string",
             "inchi_key": "inchi_key::string",
        }
        self.enrich_fields = {
            "item_id::string": "item_id::string",
            "identifier": "coco_id::string",
            "canonical_smiles": "canonical_smiles::string",
            "standard_inchi": "standard_inchi::string",
            "standard_inchi_key": "standard_inchi_key::string",
            "name": "name::string",
            "iupac_name": "iupac_name::string",
            "annotation_level": "annotation_level::string",
            "total_atom_count": "total_atom_count::number",
            "heavy_atom_count": "heavy_atom_count::number",
            "molecular_weight": "molecular_weight::number",
            "exact_molecular_weight": "exact_molecular_weight::number",
            "molecular_formula": "molecular_formula::string",
            "alogp": "alogp::number",
            "topological_polar_surface_area": "topological_polar_surface_area::number",
            "rotatable_bond_count": "rotatable_bond_count::number",
            "hydrogen_bond_acceptors": "hydrogen_bond_acceptors::number",
            "hydrogen_bond_donors": "hydrogen_bond_donors::number",
            "hydrogen_bond_acceptors_lipinski": "hydrogen_bond_acceptors_lipinski::number",
            "hydrogen_bond_donors_lipinski": "hydrogen_bond_donors_lipinski::number",
            "lipinski_rule_of_five_violations": "lipinski_rule_of_five_violations::number",
            "aromatic_rings_count": "aromatic_rings_count::number",
            "qed_drug_likeliness": "qed_drug_likeliness::number",
            "formal_charge": "formal_charge::number",
            "fractioncsp3": "fractioncsp3::number",
            "number_of_minimal_rings": "number_of_minimal_rings::number",
            "van_der_walls_volume": "van_der_walls_volume::number",
            "contains_sugar": "contains_sugar::boolean",
            "contains_ring_sugars": "contains_ring_sugars::boolean",
            "contains_linear_sugars": "contains_linear_sugars::boolean",
            "murcko_framework": "murcko_framework::string",
            "np_likeness": "np_likeness::number",
            "chemical_class": "chemical_class::string",
            "chemical_sub_class": "chemical_sub_class::string",
            "chemical_super_class": "chemical_super_class::string",
            "direct_parent_classification": "direct_parent_classification::string",
            "np_classifier_pathway": "np_classifier_pathway::string",
            "np_classifier_superclass": "np_classifier_superclass::string",
            "np_classifier_class": "np_classifier_class::string",
            "np_classifier_is_glycoside": "np_classifier_is_glycoside::boolean",
            "organisms": "organisms::string_list",
            "collections": "collections::string_list",
            "dois": "dois::string_list",
            "synonyms": "synonyms::string_list",
            "cas": "cas::string",
        }

        self.old_new_string_list_separator = ("|", "::")

class CHEMBLTrypanosoma(CHEMBL):
    def __init__(self, input_path, output_path, n_workers=1, sparql_endpoint="http://141.57.8.18:8896/sparql"):
        super().__init__(input_path, output_path, n_workers, sparql_endpoint)

    def load_item_data(self) -> pd.DataFrame:
        """
        Loads the chemical compounds (items) of the CHEMBL dataset.

        Reads ``mixed.csv`` (a drug--target binding table) and keeps every
        column except the two target columns (``Target ChEMBL ID`` and
        ``Target Type``), which describe the user side of the interactions.
        Rows are deduplicated by their ``Molecule ChEMBL ID`` so that each
        molecule becomes a single item, and a sequential ``item_id`` is
        assigned following the resulting dataframe index.

        :return: pd.DataFrame with one row per item (molecule) and a sequential
        ``item_id::string`` column.
        """
        filename = os.path.join(self.input_path, "mixed.csv")
        df = pd.read_csv(filename, sep=self.item_separator)

            # keep only the item fields (i.e. drop the two target columns)
        df = df[list(self.item_fields.keys())]

            # each molecule is a single item: drop duplicate Molecule ChEMBL IDs
        df = df.drop_duplicates("Molecule ChEMBL ID").reset_index(drop=True)

            # sequential item_id following the dataframe index
        df["item_id::string"] = df.index.astype(str)

            # standardize the remaining columns following the item_fields mapping
        df = df.rename(self.item_fields, axis=1)

            # keep item_id as the first column
        item_columns = [self.item_fields[k] for k in self.item_fields]
        df = df[["item_id::string"] + item_columns]

        return df

    def load_user_data(self) -> pd.DataFrame:
        """
        Loads the biological targets (users) of the CHEMBL dataset.

        The binding table has no dedicated user file, so the unique targets are
        extracted from the ``Target ChEMBL ID`` column of ``mixed.csv``. A
        sequential ``user_id`` is assigned following the resulting dataframe
        index.

        :return: pd.DataFrame with one row per user (target) and a sequential
        ``user_id::string`` column.
        """
        filename = os.path.join(self.input_path, "mixed.csv")
        df = pd.read_csv(filename, sep=self.user_separator)

            # extract the unique targets, each becoming a single user
        df = df[["Target ChEMBL ID", "Target Type"]].drop_duplicates(ignore_index=True)

            # sequential user_id following the dataframe index
        df["user_id::string"] = df.index.astype(str)

            # standardize the target identifier following the user_fields mapping
        df = df.rename(self.user_fields, axis=1)

                # keep user_id as the first column
        df = df[["user_id::string", self.user_fields["Target ChEMBL ID"], self.user_fields["Target Type"]]]

        return df

    def load_rating_data(self) -> pd.DataFrame:
        """
        Loads the rating interactions of the CHEMBL dataset.

        Each rating is the activity of a compound (item) in a target
        (user), read from the ``Activity`` column of ``mixed.csv``:
        ``ACTIVE`` maps to a rating of 1 and ``INACTIVE`` to 0. The
        ``Molecule ChEMBL ID`` and ``Target ChEMBL ID`` of each row are
        mapped to the sequential ``item_id`` and ``user_id`` assigned in
        the processed ``item.csv`` and ``user.csv`` files, which must
        therefore be created first. Rows whose molecule or target has no
        assigned id are dropped.

        :return: pd.DataFrame with columns ``user_id::string``,
        ``item_id::string`` and ``rating::number``.
        """
        filename = os.path.join(self.input_path, "mixed.csv")
        df = pd.read_csv(filename, sep=self.rating_separator)

        # the processed item and user files must exist beforehand
        user_filename = self.user_filename
        item_filename = self.item_filename
        if not os.path.exists(user_filename) or not os.path.exists(item_filename):
            raise ValueError(
                "User and Item files must be processed before processing the rating data."
            )

        df_user = pd.read_csv(user_filename)
        df_item = pd.read_csv(item_filename)

        # map the original ChEMBL identifiers to their sequential ids
        user_dict = dict(
            zip(
                df_user[self.user_fields["Target ChEMBL ID"]].astype(str),
                df_user["user_id::string"].astype(str),
            )
        )
        item_dict = dict(
            zip(
                df_item[self.item_fields["Molecule ChEMBL ID"]].astype(str),
                df_item["item_id::string"].astype(str),
            )
        )

        # ACTIVE -> 1, INACTIVE -> 0
        rating_dict = {field: [] for field in self.rating_fields.values()}
        for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing ratings"):
            user_id = user_dict.get(row["Target ChEMBL ID"])
            item_id = item_dict.get(row["Molecule ChEMBL ID"])

            # skip rows whose target or molecule has no assigned id
            if user_id is None or item_id is None:
                continue

            rating = 1 if row["Activity"] == "ACTIVE" else 0

            rating_dict["user_id::string"].append(user_id)
            rating_dict["item_id::string"].append(item_id)
            rating_dict["rating::number"].append(rating)

        return pd.DataFrame(rating_dict)
    
    def entity_linking(self, df_item) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "coconut_csv-10-2026.csv")
        lf = pl.scan_csv(filename)

        lf_item = pl.from_pandas(df_item).lazy()
        lazy_merge = lf_item.join(
            lf,
            left_on="inchi_key",
            right_on="standard_inchi_key",
            how="left"  # Options: 'inner', 'left', 'outer', 'semi'
        )

        df_map = lazy_merge.collect().to_pandas()
        df_map = df_map[["item_id", "identifier", "inchi_key"]].rename(columns={"identifier": "URI"})
        df_map = df_map.rename(columns=self.map_fields)
        
        return df_map

    def enrich(self, df_map) -> pd.DataFrame():
        filename = os.path.join(self.input_path, "coconut_csv-10-2026.csv")
        lf = pl.scan_csv(filename)

        lf_map = pl.from_pandas(df_map).lazy()
        lazy_merge = lf.join(
            lf_map,
            left_on="identifier",
            right_on="coco_id::string",
            how="inner"  # Options: 'inner', 'left', 'outer', 'semi'
        )

        df_enrich = lazy_merge.collect().to_pandas()
        df_enrich = (
            df_enrich[self.enrich_fields.keys()]
            .rename(columns=self.enrich_fields)
            .sort_values("item_id::string")
            .set_index("item_id::string")
        )
        # putting string_list separator to the standard
        for col in self.enrich_fields.values():
            if "string_list" in col:
                df_enrich[col] = (
                    df_enrich[col].apply(
                            lambda x: x.replace(self.old_new_string_list_separator[0], self.old_new_string_list_separator[1])
                        )
                )

        return df_enrich
