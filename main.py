import logging
import argparse 

from modules.mongoatlas import MongoAtlasConnector
from modules.neo4jaura import Neo4jAuraConnector

from scripts.extract import extract_pubmed_to_mongo
from scripts.transform.annotate import annotate_mongo_articles
from scripts.transform.clean import prepare_data_for_neo4j
from scripts.load import load_to_aura

from config.neo4jdb_config import NEO4J_LABELS, NEO4J_REL_TYPES, NEO4J_AUTH, NEO4J_URI
from config.mongodb_config import CONNECTION_STR


#exit with KeyboardInterrupt, raise other exceptions
def extract_stage(max_results=1000, extract_abstracts_only=False):
    """Step 1: Extract articles from PubMed to MongoDB."""
    try:
        logging.info("Starting extraction stage.")
        print("Starting extraction stage...")
        extract_pubmed_to_mongo(
            extract_abstracts_only=extract_abstracts_only,
            max_results=max_results
        )
        logging.info("Extraction stage completed. Data loaded to Mongo Atlas.")
        print("Extraction stage completed.")
    except KeyboardInterrupt as k:
        print("Extraction stage interrupted manually.")
        logging.exception(f"Extraction stage failed: {k}")
        exit(1)
        
    except Exception as e:
        logging.exception(f"Extraction stage failed: {e}")
        raise


def annotate_stage(ents_path="data/extracted_entities.csv",
                   rels_path="data/extracted_relations.csv"):
    """Step 2: Annotate articles (NER, RE, Linking)."""
    try:
        logging.info("Starting annotation stage.")
        print("Starting annotation stage...")
        annotate_mongo_articles(raw_ents_path=ents_path, raw_rels_path=rels_path)
        logging.info(f"Annotation stage completed. Entities: {ents_path}, Relations: {rels_path}")
        print(f"Annotation stage completed. entities: {ents_path} relations: {rels_path}")
    except KeyboardInterrupt as k:
        print("Annotation stage interrupted manually.")
        logging.exception(f"Annotation stage failed: {k}")
        exit(1)
    except Exception as e:
        logging.exception(f"Annotation stage failed: {e}")
        raise


def clean_stage(raw_ents_path="data/extracted_entities.csv",
                raw_rels_path="data/extracted_relations.csv",
                saving_dir="data/ready_for_neo4j"):
    """Step 3: Prepare data for Neo4j and return cleaned CSV paths."""
    try:
        logging.info("Starting cleaning stage.")
        print("Starting cleaning stage...")
        ents_path, rels_path = prepare_data_for_neo4j(
            raw_ents_path=raw_ents_path,
            raw_rels_path=raw_rels_path,
            saving_dir=saving_dir
        )
        logging.info(f"Cleaning stage completed. Cleaned files: {ents_path}, {rels_path}")
        print(f"Cleaning stage completed. clean entities: {ents_path} clean relations: {rels_path}")
        return ents_path, rels_path
    except KeyboardInterrupt as k:
        print("Cleaning stage interrupted manually.")
        logging.exception(f"Cleaning stage failed: {k}")
        exit(1)
    except Exception as e:
        logging.exception(f"Cleaning stage failed: {e}")
        raise



def load_stage(ents_clean_csv = 'data/ready_for_neo4j/entities4neo4j.csv', rels_clean_csv = 'data/ready_for_neo4j/relations4neo4j.csv',
               labels=NEO4J_LABELS, reltypes=NEO4J_REL_TYPES,
               load_batch_size=1000):
    """Step 4: Load entities and relations into Neo4j Aura."""
    try:
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
        print("Loading stage completed. Data loaded to Noe4j Aura.")
    except KeyboardInterrupt as k:
        print("Loading stage interrupted manually.")
        logging.exception(f"Loading stage failed: {k}")
        exit(1)
    except Exception as e:
        logging.exception(f"Loading stage failed: {e}")
        raise



def run_etl(clean_dbs = False, max_results=1000,
            extract_abstracts_only=False,
            load_batch_size=1000):
    """WARNING: calling this with clean_dbs = True will delete ALL Mongo Atlas docs 
                and ALL Neo4j Aura nodes and relationships"""
    if clean_dbs:
        mongo_connector = MongoAtlasConnector(CONNECTION_STR)
        mongo_connector.delete_collection_content()
        with Neo4jAuraConnector(uri=NEO4J_URI,auth=NEO4J_AUTH) as connector:
            connector.delete_graph_content()


    """Full ETL pipeline orchestrator."""
    try:
        extract_stage(max_results=max_results, extract_abstracts_only=extract_abstracts_only)
        annotate_stage()
        ents_path, rels_path = clean_stage()
        load_stage(ents_clean_csv=ents_path, rels_clean_csv=rels_path,
                   load_batch_size=load_batch_size)
        logging.info("ETL pipeline completed successfully.")

    except Exception as e:
        logging.exception(f"ETL pipeline failed: {e}")
        raise 


#transform into CLI
######### in terminal #########
# python main.py calls the run_etl()
# python main.py step (with step in ["extract", "clean", "annotate", "load"]) calls step_stage()
# exp: python main.py extract --> calls extract_stage() 
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("step", nargs="?", choices=["extract", "annotate", "clean", "load"])
    args = parser.parse_args()

    if args.step == "extract":
        extract_stage()
    elif args.step == "annotate":
        annotate_stage()
    elif args.step == "clean":
        clean_stage()
    elif args.step == "load":
        load_stage()
    else: 
        run_etl()