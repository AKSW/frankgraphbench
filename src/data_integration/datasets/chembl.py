import os
import queue
import re
from collections import defaultdict
from io import BytesIO
from string import Template

import pandas as pd
from pandas.errors import EmptyDataError
from SPARQLWrapper import CSV
from tqdm import tqdm

from ..dataset import Dataset


def _add_sparql_escape(name_str) -> str:
    escaped = re.escape(name_str)
    return escaped.replace("\\", "\\\\")


def _get_template_query(param, p_type) -> str:
    templates = {
        "inchi_key": Template(
             """
             ?molecule_id coco:standardInchiKey ?inchi_key .
            FILTER regex(?inchi_key, "$inchi_key", "i")
             """
         ),
        "inchi": Template(
             """
             ?molecule_id coco:standardInchi ?inchi .
            FILTER regex(?inchi, "$inchi", "i")
             """
         ),
        "iupac_name": Template(
             """
             ?molecule_id coco:iupacName ?iupacName .
            FILTER regex(?iupacName, "$iupac_name", "i")
             """
         ),
    }
    if isinstance(param, str):
        return templates[p_type].substitute({p_type: _add_sparql_escape(param)})
    else:
        return ""


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
              "Molecular Weight": "molecular_weight::float",
              "#RO5 Violations": "#ro5_violations::float",
              "AlogP": "alogp::float",
              "Smiles": "smiles::string",
              "Standard Relation": "standard_relation::string",
              "Value(nM)": "value(nM)::float",
            #   "Activity": "Activity::string",
            #   "Unnamed: 0.2": "Unnamed: 0.2::integer",
              "CID": "cid::integer",
              "MolecularFormula": "molecular_formula::string",
              "MolecularWeight": "molecular_weight::float",
              "SMILES": "smiles::string",
              "InChI": "inchi::string",
              "InChIKey": "inchi_key::string",
              "IUPACName": "iupac_name::string",
              "TPSA": "tpsa::float",
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
             "URI": "URI::string",
             "inchi_key": "inchi_key::string",
        }
        self.map_query_template = Template(
             """
            PREFIX coco: <http://coconutKG.aksw.org/ontology#>
            PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl:  <http://www.w3.org/2002/07/owl#>
            PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>

            SELECT DISTINCT ?molecule WHERE {
                ?molecule a coco:Molecule .
                ?molecule coco:labeledBy ?molecule_id .
                {
                    $inchi_key_template
                } UNION {
                    $inchi_template
                } UNION {
                    $iupac_name_template
                }
            }
         """
        )
        self.enrich_fields = {
             "item_id": "item_id::string",
             "URI": "URI::string",
             "moleculeName": "molecule_name::string",
             "iupacName": "iupac_name::string",
             "canonicalSmiles": "canonical_smiles::string",
             "standardInchi": "standard_inchi::string",
             "standardInchiKey": "standard_inchi_key::string",
             "sugarFreeSmiles": "sugar_free_smiles::string",
             "moleculeIdentifier": "molecule_identifier::string",
             "annotationLevel": "annotation_level::string",
             "comment": "comment::string",
             "nameTrustLevel": "name_trust_level::string",
             "structuralComments": "structural_comments::string",
             "synonyms": "synonyms::string",
             "hasStereo": "has_stereo::string",
             "hasVariants": "has_variants::string",
             "isParent": "is_parent::string",
             "isTautomer": "is_tautomer::string",
             "parentMolecule": "parent_molecule::string",
             "chemicalClass": "chemical_class::string",
             "chemicalSubClass": "chemical_sub_class::string",
             "chemicalSuperClass": "chemical_super_class::string",
             "molecularFormula": "molecular_formula::string",
             "molecularWeight": "molecular_weight::float",
             "npLikeness": "np_likeness::float",
             "fractioncsp3": "fractioncsp3::float",
             "directParentClassification": "direct_parent_classification::string",
             "exactMolecularWeight": "exact_molecular_weight::float",
             "heavyAtomCount": "heavy_atom_count::integer",
             "totalAtomCount": "total_atom_count::integer",
             "vanDerWallsVolume": "van_der_walls_volume::float",
             "AlogP": "AlogP::float",
             "formalCharge": "formal_charge::integer",
             "hydrogenBondAcceptors": "hydrogen_bond_acceptors::integer",
             "hydrogenBondDonors": "hydrogen_bond_donors::integer",
             "qedDrugLikeliness": "qed_drug_likeliness::float",
             "LipinskiRuleOfFiveViolations": "lipinski_rule_of_five_violations::integer",
             "hydrogenBondAcceptorsLipinski": "hydrogen_bond_acceptors_lipinski::integer",
             "hydrogenBondDonorsLipinski": "hydrogen_bond_donors_lipinski::integer",
             "aromaticRingCount": "aromatic_ring_count::integer",
             "containsLinearSugars": "contains_linear_sugars::boolean",
             "containsRingSugars": "contains_ring_sugars::boolean",
             "containsSugar": "contains_sugar::boolean",
             "murkoFramework": "murko_framework::string",
             "numberOfMinimalRings": "number_of_minimal_rings::integer",
             "rotatableBondCount": "rotatable_bond_count::integer",
             "topologicalPolarSurfaceArea": "topological_polar_surface_area::float",
        }
        self.enrich_query_template = Template(
            """
            PREFIX coco: <http://coconutKG.aksw.org/ontology#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT DISTINCT
                 ?moleculeName ?iupacName ?canonicalSmiles ?standardInchi ?standardInchiKey ?sugarFreeSmiles ?moleculeIdentifier
                 ?annotationLevel ?comment ?nameTrustLevel ?structuralComments ?synonyms
                 ?hasStereo ?hasVariants ?isParent ?isTautomer ?parentMolecule
                 ?chemicalClass ?chemicalSubClass ?chemicalSuperClass ?molecularFormula ?molecularWeight ?npLikeness ?fractioncsp3 ?directParentClassification
                 ?exactMolecularWeight ?heavyAtomCount ?totalAtomCount ?vanDerWallsVolume
                 ?AlogP ?formalCharge ?hydrogenBondAcceptors ?hydrogenBondDonors ?qedDrugLikeliness ?LipinskiRuleOfFiveViolations ?hydrogenBondAcceptorsLipinski ?hydrogenBondDonorsLipinski
                 ?aromaticRingCount ?containsLinearSugars ?containsRingSugars ?containsSugar ?murkoFramework ?numberOfMinimalRings ?rotatableBondCount ?topologicalPolarSurfaceArea
            WHERE {
                VALUES ?molecule { <$URI> }

                OPTIONAL { ?molecule coco:labeledBy ?identifier }
                OPTIONAL { ?identifier coco:moleculeName ?moleculeName }
                OPTIONAL { ?identifier coco:iupacName ?iupacName }
                OPTIONAL { ?identifier coco:canonicalSmiles ?canonicalSmiles }
                OPTIONAL { ?identifier coco:standardInchi ?standardInchi }
                OPTIONAL { ?identifier coco:standardInchiKey ?standardInchiKey }
                OPTIONAL { ?identifier coco:sugarFreeSmiles ?sugarFreeSmiles }
                OPTIONAL { ?identifier coco:moleculeIdentifier ?moleculeIdentifier }

                OPTIONAL { ?molecule coco:isExplainedThrough ?descriptiveInfo }
                OPTIONAL { ?descriptiveInfo coco:annotationLevel ?annotationLevel }
                OPTIONAL { ?descriptiveInfo coco:comment ?comment }
                OPTIONAL { ?descriptiveInfo coco:nameTrustLevel ?nameTrustLevel }
                OPTIONAL { ?descriptiveInfo coco:structuralComments ?structuralComments }
                OPTIONAL { ?descriptiveInfo coco:synonyms ?synonyms }

                OPTIONAL { ?molecule coco:classifiedBy ?classification }
                OPTIONAL { ?classification coco:hasStereo ?hasStereo }
                OPTIONAL { ?classification coco:hasVariants ?hasVariants }
                OPTIONAL { ?classification coco:isParent ?isParent }
                OPTIONAL { ?classification coco:isTautomer ?isTautomer }
                OPTIONAL { ?classification coco:parentMolecule ?parentMolecule }

                OPTIONAL { ?molecule coco:describedBy ?properties }

                OPTIONAL { ?properties rdf:type coco:ConstitutionalDescriptor }
                OPTIONAL { ?properties coco:chemicalClass ?chemicalClass }
                OPTIONAL { ?properties coco:chemicalSubClass ?chemicalSubClass }
                OPTIONAL { ?properties coco:chemicalSuperClass ?chemicalSuperClass }
                OPTIONAL { ?properties coco:molecularFormula ?molecularFormula }
                OPTIONAL { ?properties coco:molecularWeight ?molecularWeight }
                OPTIONAL { ?properties coco:npLikeness ?npLikeness }
                OPTIONAL { ?properties coco:fractioncsp3 ?fractioncsp3 }
                OPTIONAL { ?properties coco:directParentClassification ?directParentClassification }

                OPTIONAL { ?properties rdf:type coco:GeometricalDescriptor }
                OPTIONAL { ?properties coco:exactMolecularWeight ?exactMolecularWeight }
                OPTIONAL { ?properties coco:heavyAtomCount ?heavyAtomCount }
                OPTIONAL { ?properties coco:totalAtomCount ?totalAtomCount }
                OPTIONAL { ?properties coco:vanDerWallsVolume ?vanDerWallsVolume }

                OPTIONAL { ?properties rdf:type coco:ElectronicDescriptor }
                OPTIONAL { ?properties coco:AlogP ?AlogP }
                OPTIONAL { ?properties coco:formalCharge ?formalCharge }
                OPTIONAL { ?properties coco:hydrogenBondAcceptors ?hydrogenBondAcceptors }
                OPTIONAL { ?properties coco:hydrogenBondDonors ?hydrogenBondDonors }
                OPTIONAL { ?properties coco:qedDrugLikeliness ?qedDrugLikeliness }
                OPTIONAL { ?properties coco:LipinskiRuleOfFiveViolations ?LipinskiRuleOfFiveViolations }
                OPTIONAL { ?properties coco:hydrogenBondAcceptorsLipinski ?hydrogenBondAcceptorsLipinski }
                OPTIONAL { ?properties coco:hydrogenBondDonorsLipinski ?hydrogenBondDonorsLipinski }

                OPTIONAL { ?properties rdf:type coco:TopologicalDescriptor }
                OPTIONAL { ?properties coco:aromaticRingCount ?aromaticRingCount }
                OPTIONAL { ?properties coco:containsLinearSugars ?containsLinearSugars }
                OPTIONAL { ?properties coco:containsRingSugars ?containsRingSugars }
                OPTIONAL { ?properties coco:containsSugar ?containsSugar }
                OPTIONAL { ?properties coco:murkoFramework ?murkoFramework }
                OPTIONAL { ?properties coco:numberOfMinimalRings ?numberOfMinimalRings }
                OPTIONAL { ?properties coco:rotatableBondCount ?rotatableBondCount }
                OPTIONAL { ?properties coco:topologicalPolarSurfaceArea ?topologicalPolarSurfaceArea }
            }
        """
        )

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
        item_columns = [self.item_fields[k] for k in self.item_fields.keys()]
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
         # drop duplicate inchi_keys
        df_item = df_item.drop_duplicates(self.item_fields["InChIKey"], ignore_index=True)

        q = queue.Queue()
        for idx, row in df_item[[self.item_fields["InChI"], self.item_fields["InChIKey"], self.item_fields["IUPACName"]]].iterrows():
            query = self.get_map_query(
                inchi_key=row[self.item_fields["InChIKey"]],
                inchi=row[self.item_fields["InChI"]],
                iupac_name=row[self.item_fields["IUPACName"]],
            )
            q.put((idx, query))

        if self.n_workers > 1:
            responses = self.parallel_queries(q)
        else:
            responses = self.sequential_queries(q)

        URI_mapping = {}
        for response in tqdm(responses, desc="Disambiguating query return"):
            candidate_URIs = []
            idx, result = response
            for binding in result["results"]["bindings"]:
                URI = binding["molecule"]["value"]
                candidate_URIs.append(URI)

            if candidate_URIs:
                URI_mapping[idx] = candidate_URIs[0]

        df_map = pd.DataFrame({"item_id": df_item.index, "inchi_key": df_item[self.item_fields["InChIKey"]]})
        df_map.set_index("item_id")
        df_map["URI"] = df_map["item_id"].apply(lambda id: URI_mapping.get(id))
        df_map = df_map.rename(self.map_fields, axis=1)

        return df_map

    def get_map_query(self, inchi_key, inchi, iupac_name) -> str:
        params = {
             "inchi_key_template": _get_template_query(inchi_key, "inchi_key"),
             "inchi_template": _get_template_query(inchi, "inchi"),
             "iupac_name_template": _get_template_query(iupac_name, "iupac_name"),
        }
        query = self.map_query_template.substitute(**params)
        return query

    def get_enrich_query(self, URI) -> str:
        params = {"URI": URI}
        query = self.enrich_query_template.substitute(**params)
        return query

    def enrich(self, df_map) -> pd.DataFrame():
        df_map = df_map[df_map[self.map_fields["URI"]].notna()]

        q = queue.Queue()
        for _, row in df_map[[self.map_fields["URI"], self.map_fields["item_id"]]].iterrows():
            query = self.get_enrich_query(row[self.map_fields["URI"]])
            q.put((row[self.map_fields["item_id"]], query))

        if self.n_workers > 1:
            responses = self.parallel_queries(q, CSV)
        else:
            responses = self.sequential_queries(q, CSV)

        item_enriching = defaultdict(dict)
        for response in responses:
            idx, result = response

             # skip empty or malformed SPARQL responses instead of crashing
            if not result:
                print(f"Empty response for item {idx}, skipping.")
                continue

            try:
                df = pd.read_csv(BytesIO(result))
            except EmptyDataError:
                print(f"Empty result for item {idx}, skipping.")
                continue

            if df.shape[0] > 1:
                print("At least one property has more than one value!")
                print(df.value_counts(dropna=False))

            try:
                item_enriching[idx] = df.iloc[0]    # getting pd.Series
            except Exception as e:
                print(f"Error at item {idx}: {e}")
                print(df)
                continue

        df_enrich = pd.DataFrame.from_dict(item_enriching, orient="index")
        df_enrich = df_enrich.rename(self.enrich_fields, axis=1)
        df_enrich.index.name = self.enrich_fields["item_id"]

        return df_enrich
