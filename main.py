import logging

from scripts.extract import extract_pubmed_to_mongo
from scripts.transform.annotate import annotate_mongo_articles
from scripts.transform.clean import prepare_data_for_neo4j
from scripts.load import load_to_aura
from config.neo4jdb_config import NEO4J_LABELS, NEO4J_REL_TYPES



def extract_stage(max_results=1000, extract_abstracts_only=True):
    """Step 1: Extract articles from PubMed to MongoDB."""
    logging.info("Starting extraction stage.")
    print("Starting extraction stage...")
    extract_pubmed_to_mongo(
        extract_abstracts_only=extract_abstracts_only,
        max_results=max_results
    )
    logging.info("Extraction stage completed.")
    print("Extraction stage completed.")

def annotate_stage(ents_path="data/extracted_entities.csv",
                   rels_path="data/extracted_relations.csv"):
    """Step 2: Annotate articles (NER, RE, Linking)."""
    logging.info("Starting annotation stage.")
    print("Starting annotation stage...")
    annotate_mongo_articles(ents_path=ents_path, rels_path=rels_path)
    logging.info(f"Annotation stage completed. Entities: {ents_path}, Relations: {rels_path}")
    print("Annotation stage completed.")

def clean_stage(raw_ents_path="data/extracted_entities.csv",
                raw_rels_path="data/extracted_relations.csv",
                saving_dir="data/ready_for_neo4j"):
    """Step 3: Prepare data for Neo4j and return cleaned CSV paths."""
    logging.info("Starting cleaning stage.")
    print("Starting cleaning stage...")
    ents_path, rels_path = prepare_data_for_neo4j(
        raw_ents_path=raw_ents_path,
        raw_rels_path=raw_rels_path,
        saving_dir=saving_dir
    )
    logging.info(f"Cleaning stage completed. Cleaned files: {ents_path}, {rels_path}")
    print("Cleaning stage completed.")
    return ents_path, rels_path


def load_stage(ents_clean_csv, rels_clean_csv,
               labels=NEO4J_LABELS, reltypes=NEO4J_REL_TYPES,
               load_batch_size=1000):
    """Step 4: Load entities and relations into Neo4j Aura."""
    logging.info("Starting loading stage.")
    print("Starting loading stage...")
    load_to_aura(
        labels_to_load=labels,
        ents_clean_csv=ents_clean_csv,
        reltypes_to_load=reltypes,
        rels_clean_csv=rels_clean_csv,
        load_batch_size=load_batch_size
    )
    logging.info("Loading stage completed.")
    print("Loading stage completed.")

def run_etl(max_results=1000,
            extract_abstracts_only=True,
            load_batch_size=1000):
    """Full ETL pipeline orchestrator."""
    try:
        extract_stage(max_results=max_results, extract_abstracts_only=extract_abstracts_only)
        annotate_stage()
        ents_path, rels_path = clean_stage()
        load_stage(ents_clean_csv=ents_path, rels_clean_csv=rels_path,
                   load_batch_size=load_batch_size)
        logging.info("ETL pipeline completed successfully.")
    except KeyboardInterrupt as k:
        print("ETL interrupted manually.")
        logging.exception(f"ETL pipeline failed: {k}")
    except Exception as e:
        logging.exception(f"ETL pipeline failed: {e}")
        raise


if __name__ == "__main__":
    run_etl()
