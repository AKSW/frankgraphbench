import argparse
import logging
import queue
import re
import string
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import pandas as pd
from SPARQLWrapper import CSV, JSON, SPARQLWrapper
from tqdm import tqdm

from worker import EndpointQueryError, Worker

SPARQL_ENDPOINT = "http://141.57.8.18:8891/sparql"
TIMEOUT = 1000
MAX_RETRIES = 5
CHUNK_SIZE = 500
NUM_CHUNK_WORKERS = 2

logger = logging.getLogger(__name__)

MAP_QUERY_TEMPLATE = string.Template(
    """
    PREFIX coco:   <http://coconutKG.aksw.org/ontology#>
    PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl:    <http://www.w3.org/2002/07/owl#>
    PREFIX xsd:    <http://www.w3.org/2001/XMLSchema#>

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
MAP_FIELDS = {
    "item_id": "item_id::string",
    "URI": "URI::string",
    "inchi_key": "inchi_key::string",
}

ENRICH_QUERY_TEMPLATE = string.Template(
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
ENRICH_FIELDS = {
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


def _query(query, return_type=JSON, max_retries=MAX_RETRIES) -> dict:
    """
    Query the SPARQL endpoint, retrying on any connection or endpoint error.

    Retries up to `max_retries` times. If every attempt fails, the query is
    aborted by raising `EndpointQueryError`, which propagates up to stop the
    entire execution.
    """
    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            sparql = SPARQLWrapper(SPARQL_ENDPOINT)
            sparql.setTimeout(TIMEOUT)
            sparql.setQuery(query)
            sparql.setReturnFormat(return_type)
            return sparql.query().convert()
        except Exception as e:
            last_exception = e
            logger.warning(
                f"Query attempt {attempt}/{max_retries} failed: {e}"
            )

    raise EndpointQueryError(
        f"Query failed after {max_retries} attempts: {last_exception}"
    ) from last_exception

def parallel_queries(queue, return_type=JSON, stop_event=None):
    """
    Parallel query SPARQL endpoint using Threads.

     :arguments:
        queue: queue of tuples indicating the item_id and SPARQL query string
        stop_event: optional shared threading.Event used to abort every worker
            of this pool when another part of the run (e.g. a concurrent chunk)
            has failed irrecoverably
     :returns: list containing tuples with item_id and response result in JSON
     :raises EndpointQueryError: if any query fails after all retries, the
        whole run is aborted and only the responses gathered so far are logged
     """
    n_iters = queue.qsize()
    pbar = tqdm(total=n_iters)
    pbar.set_description("Requesting SPARQL endpoint for each item")

     # shared across every concurrent chunk so one failure aborts the whole run
    stop_event = stop_event if stop_event is not None else threading.Event()

     # create and start every worker
    workers = []
    for _ in range(8):
        worker = Worker(
            queue,
            lambda q: _query(q, return_type),
            pbar,
            stop_event=stop_event,
         )
        workers.append(worker)
    for worker in workers:
        worker.start()

     # join every worker and wait for them to finish
    for worker in workers:
        worker.join()
    pbar.close()

     # combining results
    responses = []
    for worker in workers:
        responses.extend(worker.local_results)

     # abort the whole execution if any worker failed irrecoverably
    for worker in workers:
        if worker.error is not None:
            n_unmatched = n_iters - len(responses)
            logger.error(
                f"Aborting execution: a query failed after {MAX_RETRIES} "
                f"retries. {n_unmatched} of {n_iters} items were not matched."
             )
            raise worker.error

    return responses

def sequential_queries(q, return_type=JSON):
    """
    Sequential query SPARQL endpoint.

    :arguments:
        queue: queue of tuples indicating the item_id and SPARQL query string
    :returns: list containing tuples with item_id and response result in JSON
    """
    pbar = tqdm(total=q.qsize())
    pbar.set_description("Requesting SPARQL endpoint for each item")
    responses = []

    while True:
        try:
            idx, query = q.get(block=False)
            response = _query(query, return_type)
            responses.append((idx, response))
            pbar.update(n=1)
        except queue.Empty:
            break
        except EndpointQueryError as e:
            # irrecoverable: log what we have and abort the run
            logger.error(f"Aborting execution: {e}")
            raise
        except Exception as e:
            print(f"Exception: {e}")

    return responses

def _add_sparql_escape(name_str) -> str:
    escaped = re.escape(name_str)
    return escaped.replace("\\", "\\\\")

def _get_template_query(param, p_type):
    templates = {
        "inchi_key": string.Template(
            """
            ?molecule_id coco:standardInchiKey ?inchi_key .
            FILTER regex(?inchi_key, "$inchi_key", "i")
            """
        ),
        "inchi": string.Template(
            """
            ?molecule_id coco:standardInchi ?inchi .
            FILTER regex(?inchi, "$inchi", "i")
            """
        ),
        "iupac_name": string.Template(
            """
            ?molecule_id coco:iupacName ?iupacName .
            FILTER regex(?iupacName, "$iupac_name", "i")
            """
        )
    }
    if isinstance(param, str):
        return templates[p_type].substitute({p_type: _add_sparql_escape(param)})
    else:
        return ""

def get_map_query(inchi_key, inchi, iupac_name) -> str:
    params = {
        "inchi_key_template": _get_template_query(inchi_key, "inchi_key"),
        "inchi_template": _get_template_query(inchi, "inchi"),
        "iupac_name_template": _get_template_query(iupac_name, "iupac_name")
    }
    query = MAP_QUERY_TEMPLATE.substitute(**params)
    return query

def entity_linking(df_item, stop_event=None) -> pd.DataFrame():
    q = queue.Queue()
    for idx, row in df_item[["InChI", "InChIKey", "IUPACName"]].iterrows():
        query = get_map_query(inchi_key=row["InChIKey"], inchi=row["InChI"], iupac_name=row["IUPACName"])
        q.put((idx, query))

    responses = parallel_queries(q, stop_event=stop_event)

    URI_mapping = {}
    for response in tqdm(responses, desc="disambiguating query return"):
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
    df_map = df_map.rename(MAP_FIELDS, axis=1)

    return df_map

def _link_chunk(args):
    start, chunk, stop_event = args
    df_map = entity_linking(chunk, stop_event)
    # keep item_id aligned with the original dataframe's row order
    df_map[MAP_FIELDS["item_id"]] = df_map[MAP_FIELDS["item_id"]] + start
    return df_map

def map(
    input_file="data/mixed.csv",
    output_file="data/processed/map.csv",
    chunk_size=CHUNK_SIZE,
    num_workers=NUM_CHUNK_WORKERS,
):
    # drop duplicate inchi_keys and load
    df = pd.read_csv(input_file).drop_duplicates("InChIKey", ignore_index=True)

    print("mapping InChIKeys from compounds using CoconutKG...")

    # One shared abort signal across every concurrent chunk: when any query
    # fails irrecoverably, its worker sets this event and every worker in
    # every chunk stops early, so a single failure aborts the whole run.
    stop_event = threading.Event()

    chunks = []
    for start in range(0, len(df), chunk_size):
        chunk = df.iloc[start:start + chunk_size].reset_index(drop=True)
        chunks.append((start, chunk, stop_event))

    # Process the chunks concurrently: each chunk runs its own 8-thread query
    # pool, and up to `num_workers` chunks run at once.
    chunk_results = [None] * len(chunks)
    n_chunks = 0
    if chunks:
        try:
            with ThreadPoolExecutor(max_workers=num_workers) as pool:
                for result in pool.map(_link_chunk, chunks):
                    chunk_results[n_chunks] = result
                    n_chunks += 1
                    logger.info(
                        f"Finished chunk {n_chunks} of {len(chunks)}"
                    )
        except EndpointQueryError:
             # a chunk failed irrecoverably; its error is captured via
             # stop_event below. Fall through to persist whatever completed.
            pass

    # Build the final mapping from whatever completed before any failure.
    completed = [r for r in chunk_results if r is not None]

    if stop_event.is_set():
        # A chunk failed irrecoverably: persist the results gathered so far,
        # log them, then abort the execution.
        if completed:
            combined = pd.concat(completed, ignore_index=True)
            combined.to_csv(output_file, index=False)
            n_items = combined.shape[0]
            n_unmatched = combined[MAP_FIELDS["URI"]].isna().sum()
            print(
                f"Saved {n_items} mapped items gathered so far to "
                f"{output_file}; {n_unmatched} were unmatched "
                f"({n_unmatched/n_items*100:.2f}%)."
            )
        logger.error(
            f"Aborting execution: a query failed after {MAX_RETRIES} retries. "
            f"{n_chunks} of {len(chunks)} chunks completed."
        )
        raise EndpointQueryError(
            f"Chunk mapping aborted after {MAX_RETRIES} retries."
        )

    if not completed:
        logger.warning("No items to map; writing an empty result.")
        pd.DataFrame(columns=list(MAP_FIELDS.keys())).to_csv(
            output_file, index=False
        )
        return

    df_map = pd.concat(completed, ignore_index=True)
    df_map.to_csv(output_file, index=False)
    n_items = df_map.shape[0]
    n_unmatched = df_map[MAP_FIELDS["URI"]].isna().sum()
    print(
        f"{n_unmatched} items weren't matched, corresponding to "
        f"{n_unmatched/n_items*100:.2f}% of a total of {n_items}."
    )

def get_enrich_query(URI) -> str:
    params = {"URI": URI}
    query = ENRICH_QUERY_TEMPLATE.substitute(**params)
    return query

def _enrich_chunk(args):
    chunk, stop_event = args
    q = queue.Queue()
    for _, row in chunk[[MAP_FIELDS["URI"], MAP_FIELDS["item_id"]]].iterrows():
        query = get_enrich_query(row[MAP_FIELDS["URI"]])
        q.put((row[MAP_FIELDS["item_id"]], query))

    responses = parallel_queries(q, CSV, stop_event=stop_event)

    item_enriching = defaultdict(dict)
    for response in responses:
        idx, result = response
        df = pd.read_csv(BytesIO(result))

        if df.shape[0] > 1:
            print("At least one property has more than one value!")
            print(df.value_counts(dropna=False))

        item_enriching[idx] = df.iloc[0]  # getting pd.Series

    df_enrich = pd.DataFrame.from_dict(item_enriching, orient="index")
    df_enrich = df_enrich.rename(ENRICH_FIELDS, axis=1)
    df_enrich.index.name = ENRICH_FIELDS["item_id"]

    return df_enrich

def enrich(
    df_map,
    chunk_size=CHUNK_SIZE,
    num_workers=NUM_CHUNK_WORKERS,
):
    df_map = df_map[df_map[MAP_FIELDS["URI"]].notna()]

    print("enriching each mapped item using CoconutKG...")

      # One shared abort signal across every concurrent chunk: when any query
      # fails irrecoverably, its worker sets this event and every worker in
      # every chunk stops early, so a single failure aborts the whole run.
    stop_event = threading.Event()

    chunks = []
    for start in range(0, len(df_map), chunk_size):
        chunk = df_map.iloc[start:start + chunk_size].reset_index(drop=True)
        chunks.append((chunk, stop_event))

      # Process the chunks concurrently: each chunk runs its own 8-thread query
      # pool, and up to `num_workers` chunks run at once.
    chunk_results = [None] * len(chunks)
    n_chunks = 0
    if chunks:
        try:
            with ThreadPoolExecutor(max_workers=num_workers) as pool:
                for result in pool.map(_enrich_chunk, chunks):
                    chunk_results[n_chunks] = result
                    n_chunks += 1
                    logger.info(
                        f"Finished chunk {n_chunks} of {len(chunks)}"
                      )
        except EndpointQueryError:
              # a chunk failed irrecoverably; its error is captured via
              # stop_event below. Fall through to whatever completed.
            pass

      # Build the final enrichment from whatever completed before any failure.
    completed = [r for r in chunk_results if r is not None]

    if stop_event.is_set():
          # A chunk failed irrecoverably: log what was gathered, then abort the run.
        logger.error(
            f"Aborting execution: a query failed after {MAX_RETRIES} retries. "
            f"{n_chunks} of {len(chunks)} chunks completed."
          )
        raise EndpointQueryError(
            f"Chunk enriching aborted after {MAX_RETRIES} retries."
          )

    if not completed:
        logger.warning("No items to enrich; returning an empty result.")
        df_enrich = pd.DataFrame.from_dict({}, orient="index")
        df_enrich = df_enrich.rename(ENRICH_FIELDS, axis=1)
        df_enrich.index.name = ENRICH_FIELDS["item_id"]
        return df_enrich

    df_enrich = pd.concat(completed, ignore_index=False)
    df_enrich.index.name = ENRICH_FIELDS["item_id"]

    return df_enrich


def report_enriching(df):
        n_rows = df.shape[0]
        for col in df.columns:
            n_rows_with = df[col].notna().sum()
            print(
                f"number of entities with the property {col}: {n_rows_with} ({n_rows_with/n_rows*100:.2f}%)"
            )

def enrich_data(
    input_file="data/processed/map.csv",
    output_file="data/processed/enrich.csv",
):
        """
        Enrich each mapped item using DBpedia's resources.
        """

        try:
            df_map = pd.read_csv(input_file)
            print(
                f"Enriching each item with DBpedia resources: {output_file}"
            )
            df_enrich = enrich(df_map)
            df_enrich.to_csv(output_file)

            report_enriching(df_enrich)

        except NotImplementedError:
            print("Override enrich() method of your Dataset subclass.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(
        description="Map and enrich InChIKeys from compounds using CoconutKG."
    )
    parser.add_argument(
        "--map",
        action="store_true",
        help="Run the entity-linking step (map InChIKeys to CoconutKG URIs).",
    )
    parser.add_argument(
        "--enrich",
        action="store_true",
        help="Run the enrichment step (enrich mapped items with CoconutKG).",
    )
    parser.add_argument(
        "--map-input",
        default="data/mixed.csv",
        help="Input file for the mapping step (default: data/mixed.csv).",
    )
    parser.add_argument(
        "--enrich-input",
        default="data/processed/map.csv",
        help="Input file for the enrichment step (default: data/processed/map.csv).",
    )
    args = parser.parse_args()

    if not (args.map or args.enrich):
        parser.error("specify at least one of --map or --enrich")

    if args.map:
        map(input_file=args.map_input)

    if args.enrich:
        enrich_data(input_file=args.enrich_input)
