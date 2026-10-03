import queue
import re
from collections import defaultdict
from io import BytesIO
from string import Template

import pandas as pd
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
    def __init__(self, input_path, output_path, n_workers=1):
        super().__init__(input_path, output_path, n_workers)
        self.dataset_name = "CHEMBL"

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
             "moleculeName": "moleculeName::string",
             "iupacName": "iupacName::string",
             "canonicalSmiles": "canonicalSmiles::string",
             "standardInchi": "standardInchi::string",
             "standardInchiKey": "standardInchiKey::string",
             "sugarFreeSmiles": "sugarFreeSmiles::string",
             "moleculeIdentifier": "moleculeIdentifier::string",
             "annotationLevel": "annotationLevel::string",
             "comment": "comment::string",
             "nameTrustLevel": "nameTrustLevel::string",
             "structuralComments": "structuralComments::string",
             "synonyms": "synonyms::string",
             "hasStereo": "hasStereo::string",
             "hasVariants": "hasVariants::string",
             "isParent": "isParent::string",
             "isTautomer": "isTautomer::string",
             "parentMolecule": "parentMolecule::string",
             "chemicalClass": "chemicalClass::string",
             "chemicalSubClass": "chemicalSubClass::string",
             "chemicalSuperClass": "chemicalSuperClass::string",
             "molecularFormula": "molecularFormula::string",
             "molecularWeight": "molecularWeight::float",
             "npLikeness": "npLikeness::float",
             "fractioncsp3": "fractioncsp3::float",
             "directParentClassification": "directParentClassification::string",
             "exactMolecularWeight": "exactMolecularWeight::float",
             "heavyAtomCount": "heavyAtomCount::integer",
             "totalAtomCount": "totalAtomCount::integer",
             "vanDerWallsVolume": "vanDerWallsVolume::float",
             "AlogP": "AlogP::float",
             "formalCharge": "formalCharge::integer",
             "hydrogenBondAcceptors": "hydrogenBondAcceptors::integer",
             "hydrogenBondDonors": "hydrogenBondDonors::integer",
             "qedDrugLikeliness": "qedDrugLikeliness::float",
             "LipinskiRuleOfFiveViolations": "LipinskiRuleOfFiveViolations::integer",
             "hydrogenBondAcceptorsLipinski": "hydrogenBondAcceptorsLipinski::integer",
             "hydrogenBondDonorsLipinski": "hydrogenBondDonorsLipinski::integer",
             "aromaticRingCount": "aromaticRingCount::integer",
             "containsLinearSugars": "containsLinearSugars::boolean",
             "containsRingSugars": "containsRingSugars::boolean",
             "containsSugar": "containsSugar::boolean",
             "murkoFramework": "murkoFramework::string",
             "numberOfMinimalRings": "numberOfMinimalRings::integer",
             "rotatableBondCount": "rotatableBondCount::integer",
             "topologicalPolarSurfaceArea": "topologicalPolarSurfaceArea::float",
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

    def entity_linking(self, df_item) -> pd.DataFrame():
         # drop duplicate inchi_keys
        df_item = df_item.drop_duplicates("InChIKey", ignore_index=True)

        q = queue.Queue()
        for idx, row in df_item[["InChI", "InChIKey", "IUPACName"]].iterrows():
            query = self.get_map_query(
                inchi_key=row["InChIKey"],
                inchi=row["InChI"],
                iupac_name=row["IUPACName"],
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

        df_map = pd.DataFrame({"item_id": df_item.index, "inchi_key": df_item["InChIKey"]})
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
            df = pd.read_csv(BytesIO(result))

            if df.shape[0] > 1:
                print("At least one property has more than one value!")
                print(df.value_counts(dropna=False))

            try:
                item_enriching[idx] = df.iloc[0]   # getting pd.Series
            except Exception as e:
                print(f"Error at item {idx}: {e}")
                print(df)
                continue

        df_enrich = pd.DataFrame.from_dict(item_enriching, orient="index")
        df_enrich = df_enrich.rename(self.enrich_fields, axis=1)
        df_enrich.index.name = self.enrich_fields["item_id"]

        return df_enrich
