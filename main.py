import logging
import argparse
import sys

from scripts.extract import extract_pubmed_to_mongo
from scripts.transform.annotate import annotate_mongo_articles
from scripts.transform.clean import prepare_data_for_neo4j
from scripts.load import load_to_aura

from config.neo4jdb_config import NEO4J_LABELS, NEO4J_REL_TYPES

def extract_stage(max_results=1000, extract_abstracts_only=True):
    """Step 1: Extract articles from PubMed to MongoDB."""
    try:
        logging.info("Starting extraction stage.")
        print("Starting extraction stage...")
        extract_pubmed_to_mongo(
            extract_abstracts_only=extract_abstracts_only,
            max_results=max_results
        )
        logging.info("Extraction stage completed.")
        print("Extraction stage completed.")
        return True
    except KeyboardInterrupt:
        print("Extraction stage interrupted manually.")
        logging.warning("Extraction stage interrupted manually.")
        return False
    except Exception as e:
        print(f"Extraction stage failed: {e}")
        logging.exception(f"Extraction stage failed: {e}")
        return False



def annotate_stage(ents_path="data/extracted_entities.csv", rels_path="data/extracted_relations.csv"):
    """Step 2: Annotate articles (NER, RE, Linking)."""
    try:
        logging.info("Starting annotation stage.")
        print("Starting annotation stage...")
        annotate_mongo_articles(ents_path=ents_path, rels_path=rels_path)
        logging.info(f"Annotation stage completed. Entities: {ents_path}, Relations: {rels_path}")
        print("Annotation stage completed.")
        return True
    except KeyboardInterrupt:
        print("Annotation stage interrupted manually.")
        logging.warning("Annotation stage interrupted manually.")
        return False
    except Exception as e:
        print(f"Annotation stage failed: {e}")
        logging.exception(f"Annotation stage failed: {e}")
        return False



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
        print("Cleaning stage completed.")
        return ents_path, rels_path
    except KeyboardInterrupt:
        print("Cleaning stage interrupted manually.")
        logging.warning("Cleaning stage interrupted manually.")
        return None, None
    except Exception as e:
        print(f"Cleaning stage failed: {e}")
        logging.exception(f"Cleaning stage failed: {e}")
        return None, None



def load_stage(ents_clean_csv='data/ready_for_neo4j/entities4neo4j.csv',
               rels_clean_csv='data/ready_for_neo4j/relations4neo4j.csv',
               labels=NEO4J_LABELS,
               reltypes=NEO4J_REL_TYPES,
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
        print("Loading stage completed.")
        return True
    except KeyboardInterrupt:
        print("Loading stage interrupted manually.")
        logging.warning("Loading stage interrupted manually.")
        return False
    except Exception as e:
        print(f"Loading stage failed: {e}")
        logging.exception(f"Loading stage failed: {e}")
        return False



def run_etl(max_results=1000, extract_abstracts_only=True, load_batch_size=1000):
    """Full ETL pipeline orchestrator."""
    try:
        # Step 1: Extract
        print("=" * 50)
        print("ETL PIPELINE STARTING")
        print("=" * 50)
        
        if not extract_stage(max_results=max_results, extract_abstracts_only=extract_abstracts_only):
            print("ETL pipeline stopped: Extraction stage failed or was interrupted.")
            logging.error("ETL pipeline stopped: Extraction stage failed or was interrupted.")
            return False
        
        # Step 2: Annotate
        if not annotate_stage():
            print("ETL pipeline stopped: Annotation stage failed or was interrupted.")
            logging.error("ETL pipeline stopped: Annotation stage failed or was interrupted.")
            return False
        
        # Step 3: Clean
        ents_path, rels_path = clean_stage()
        if not ents_path or not rels_path:
            print("ETL pipeline stopped: Cleaning stage failed or was interrupted.")
            logging.error("ETL pipeline stopped: Cleaning stage failed or was interrupted.")
            return False
        
        # Step 4: Load
        if not load_stage(ents_clean_csv=ents_path, rels_clean_csv=rels_path, load_batch_size=load_batch_size):
            print("ETL pipeline stopped: Loading stage failed or was interrupted.")
            logging.error("ETL pipeline stopped: Loading stage failed or was interrupted.")
            return False
        
        print("=" * 50)
        print("ETL PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 50)
        logging.info("ETL pipeline completed successfully.")
        return True
        
    except KeyboardInterrupt:
        print("\nETL pipeline interrupted manually.")
        logging.warning("ETL pipeline interrupted manually.")
        return False
    except Exception as e:
        print(f"ETL pipeline failed with unexpected error: {e}")
        logging.exception(f"ETL pipeline failed: {e}")
        return False



def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Medical Graph ETL Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run full ETL pipeline
  python main.py extract            # Run only extraction stage
  python main.py annotate           # Run only annotation stage
  python main.py clean              # Run only cleaning stage
  python main.py load               # Run only loading stage
        """
    )
    
    parser.add_argument(
        "step", 
        nargs="?", 
        choices=["extract", "annotate", "clean", "load"],
        help="Run a specific ETL stage (omit to run full pipeline)"
    )
    
    parser.add_argument(
        "--max-results",
        type=int,
        default=1000,
        help="Maximum number of results to extract per API call (default: 1000, max: 10000)." \
        "Note: This is not the maximum number of results to extract, which is the hardcoded API limit 10000."
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Batch size for loading nodes and relationships to Neo4j (default: 1000)"
    )
    
    parser.add_argument(
        "--full-text",
        action="store_true",
        help="Extract full text instead of abstracts only"
    )
    
    args = parser.parse_args()
    
    success = False
    
    try:
        if args.step == "extract":
            success = extract_stage(
                max_results=args.max_results,
                extract_abstracts_only=not args.full_text
            )
        elif args.step == "annotate":
            success = annotate_stage()
        elif args.step == "clean":
            ents_path, rels_path = clean_stage()
            success = bool(ents_path and rels_path)
            if success:
                print(f"Cleaned files ready: {ents_path}, {rels_path}")
        elif args.step == "load":
            success = load_stage(load_batch_size=args.batch_size)
        else:
            success = run_etl(
                max_results=args.max_results,
                extract_abstracts_only=not args.full_text,
                load_batch_size=args.batch_size
            )
    
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        logging.warning("Process interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        logging.exception("Unexpected error occurred")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)



if __name__ == "__main__":
    main()