from typing import Optional

import logging

from modules.neo4jaura import Neo4jAuraConnector
from config.neo4jdb_config import NEO4J_AUTH, NEO4J_URI



def load_to_aura(labels_to_load:Optional[list[str]] = None,
                ents_clean_csv:Optional[str]= None,

                reltypes_to_load:Optional[list[str]] = None,
                rels_clean_csv:Optional[str] = None,

                load_batch_size = 1000):
    
        nodes_args_provided = bool(labels_to_load) and bool(ents_clean_csv)
        rels_args_provided = bool(reltypes_to_load) and bool(rels_clean_csv) 
        
        if not (nodes_args_provided or rels_args_provided):
            logging.error("Must provide either (labels_to_load AND ents_clean_csv) or (reltypes_to_load AND rels_clean_csv) or both")
            raise ValueError("Must provide either (labels_to_load AND ents_clean_csv) or (reltypes_to_load AND rels_clean_csv) or both")

        try:
            with Neo4jAuraConnector(uri=NEO4J_URI,
                                    auth=NEO4J_AUTH,
                                    load_batch_size=load_batch_size) as connector:
                if nodes_args_provided:
                    connector.load_ents_to_aura(labels_to_load, ents_clean_csv)
                
                if rels_args_provided: 
                    connector.load_rels_to_aura(reltypes_to_load, rels_clean_csv)
        
        except KeyboardInterrupt:
            logging.error("Load Process Interrupted Manually.")
            raise
        except Exception as e:
            logging.error(f"Load Process Failed To Load To Aura. {e}")
    
        