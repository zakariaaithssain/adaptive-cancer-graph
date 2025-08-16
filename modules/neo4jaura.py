#TODO: add logs, tqdms with desc argument, and use Google Docstring format for documentation 
# or maybe let the documentation till I finish the whole project and document for once. 

import pandas as pd

from neo4j import GraphDatabase, Transaction
from neo4j.exceptions import Neo4jError
from typing import List, Dict

import tqdm
import logging

from config.neo4jdb_config import NEO4J_LABELS, NEO4J_REL_TYPES

"""to load data to neo4j, we have multiple options:
    1 - load every entity or relation independently from others. 
    pros: allows dynamic labels and relations types.
    cons: not memory efficient (loops) nor network efficient 
          (1entity or relation/transaction
    2 - use CYPHER methods (either UNWIND or LOAD CSV)
    pros: memory efficient (UNWIND loads a batch, LOAD CSV loads an entire csv at once)
          network efficient (UNWIND: a batch in one connection, LOAD CSV I think the 
          whole csv in one connection)
    cons: uses plain cypher so no formatting is possible for dynamic labels 
    and relations types. this can be fixed via APOC, but it's not available for N4J Aura. 
    3 - I want dynamic labels and relation types, and I want efficiency, 
    so I will load each entity or relation type separately using cypher's UNWIND 
    (especially that I already know the entities and rels recognized by the model!!!!). 
      """



class Neo4jAuraConnector:
    def __init__(self, uri: str, auth: tuple, load_batch_size = 1000):
        """I am using Neo4j Aura Free, so I cannot create databases, 
            it uses the default one"""
        self.driver = GraphDatabase.driver(uri, auth=auth, database='neo4j')
        self.load_batch_size = load_batch_size

    #dunder methods for context management
    def __enter__(self):
        try: 
            with self.driver.session() as session: 
                result = session.run("RETURN 1 AS test")
                logging.info("AuraConnector: Successfully Connected To Neo4j Aura.")
        except Exception as e: 
                logging.error(f"AuraConnector: Connection Failed: {e}")
        finally:
            self.driver.close()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver: self.driver.close()
        return False #meaning that we allow exceptions propagation, True suppresses them I guess



    def load_ents_to_aura(self, labels_to_load : list[str], clean_csv: str):
        assert all(label in NEO4J_LABELS for label in labels_to_load), f"labels_to_load passed contains label(s) that are not among {NEO4J_LABELS}"
        """Load entities from the cleaned ents csv to Neo4j Aura. 
        Parameters:
            labels_to_load = list of the entities recognized by the NER model
            that we want to load. (exp: 'GENE')
            clean_csv = path of the cleaned ents csv."""
        #one session for more efficiency
        with self.driver.session() as session:
                for label in labels_to_load: 
                    #one transaction per entity
                    with session.begin_transaction() as transaction: 
                        nodes_with_label = self._get_nodes_with_label(label,clean_csv)
                        self._ents_batch_load(label, nodes_list=nodes_with_label, transaction= transaction)
            

    
    def load_rels_to_aura(self, reltypes_to_load : list[str], clean_csv: str):
        """Load entities from the cleaned rels csv to Neo4j Aura. 
        Parameters:
            labels_to_load = list of the entities recognized by the NER model
            that we want to load. (exp: 'GENE')
            clean_csv = path of the cleaned rels csv."""
        
        assert all(reltype in NEO4J_REL_TYPES for reltype in reltypes_to_load), f" reltypes_to_load passed contains relation type(s) that are not among {NEO4J_REL_TYPES}"
        with self.driver.session() as session:
            for reltype in reltypes_to_load: 
                with session.begin_transaction() as transaction: 
                    relations_with_reltype = self._get_relations_with_type(reltype, clean_csv)
                    self._rels_batch_load(reltype,relations_list=relations_with_reltype, transaction = transaction)





    def _ents_batch_load(self, label: str, nodes_list: List[Dict], transaction : Transaction):
        """Entities (nodes) Batch load using UNWIND for optimal performance
        Parameters:
        label = "the label for the nodes to load. (exp 'GENE')
        nodes_list = list containing nodes to load, each is a dict.
        transaction = neo4j transaction instance

        """
        
        query = f"""
            UNWIND $batch AS row
            MERGE (n:{label} {{id: row.id}})
            SET n += {{
                name: row.name,
                cui: row.cui,
                normalized_name: row.normalized_name,
                normalization_source: row.normalization_source,
                url: row.url
            }}
            """
        try: 
            for i in range(0, len(nodes_list), self.load_batch_size):
                batch = nodes_list[i:i + self.load_batch_size]
                transaction.run(query, {"batch":batch})
        except Neo4jError as ne:
            print(f"Neo4j error in batch {i//self.load_batch_size}: {ne}")
            raise
        except Exception as e:
            print(f"Unexpected error in batch {i//self.load_batch_size}: {e}")
            raise
        
    def _rels_batch_load(self, relation_type: str, relations_list: List[Dict], transaction : Transaction):
        """Relations Batch load using UNWIND for optimal performance
        Parameters:
        relation_type = "the relation_type for the relations to load. (exp 'GENE')
        relations_list: list containing relations to load, each is a dict.
        transaction: neo4j transaction instance

        """
        
        query = f"""
        UNWIND $batch AS row
        MATCH (start {{id: row.start_id}})
        MATCH (end {{id: row.end_id}})
        MERGE (start)-[r:{relation_type}]->(end)
        SET r += {{
        pmid: row.pmid,
        pmcid: row.pmcid,
                 }}
        """

        try: 
            for i in range(0, len(relations_list), self.load_batch_size):
                batch = relations_list[i:i + self.load_batch_size]
                transaction.run(query, {"batch":batch})
        except Neo4jError as ne:
            print(f"Neo4j error in batch {i//self.load_batch_size}: {ne}")
            raise
        except Exception as e:
            print(f"Unexpected error in batch {i//self.load_batch_size}: {e}")
            raise
            

    
    def _get_nodes_with_label(self, label : str, clean_csv : str):
        """ return list[dict] containing rows with 
        the same label specified in the label argument, from the global cleaned
        csv that contains all extracted entities.
        Parameters: 
                label = the label of the entities we wish to extract (exp. 'GENE') """
        # Read and preprocess data
        assert label in NEO4J_LABELS, f"label argument got {label}, not one of {NEO4J_LABELS}."
        try: 
            df = pd.read_csv(clean_csv)
        except FileNotFoundError:
            print(f"the global cleaned csv not found in {clean_csv}")
            raise
        
        try:
            entities = df[df[":LABEL"] == label].copy()
        except KeyError:
            print("':LABEL' not found in columns, perhaps you renamed it or specified another name during cleaning or extraction. " )
            raise

        if not entities.empty: 
            #format for Neo4j
            entities.rename(columns={":ID": "id"}, inplace=True, errors='ignore')
            #those will just create redundancy in the graph if kept
            to_drop = [col for col in [":LABEL", "pmid", "pmcid", "fetching_date"] if col in entities.columns]
            entities.drop(columns=to_drop, inplace=True)
            entities_dict = entities.to_dict("records")  #convert to list of dicts
            return entities_dict
        else:
            print(f"No {label} nodes found in {clean_csv}.")
            return []
        
    def _get_relations_with_type(self, type : str, clean_csv : str):
        """ return list[dict] containing relations with 
        the same type specified in the type argument, from the global cleaned
        csv that contains all extracted relations.
        Parameters: 
                type = the type of the relations we wish to extract (exp. 'AFFECTS')
                 clean_csv = the csv containing the cleaned relations."""
        
        assert type in NEO4J_REL_TYPES, f"type argument got {type}, not one of {NEO4J_REL_TYPES}."
        try: 
            df = pd.read_csv(clean_csv)
        except FileNotFoundError:
            print(f"the global cleaned csv not found in {clean_csv}")
            raise
        
        try:
            relations = df[df[":TYPE"] == type].copy()
        except KeyError:
            print("':TYPE' not found in columns, perhaps you renamed it or specified another name during cleaning or extraction. " )
            raise

        if not relations.empty: 
            #format for Neo4j
            relations.rename(columns={":ID": "id"}, inplace=True, errors='ignore')
            #those will just create redundancy in the graph if kept
            to_drop = [col for col in [":TYPE", "pmid", "pmcid", "fetching_date"] if col in relations.columns]
            relations.drop(columns=to_drop, inplace=True)
            relations_dict = relations.to_dict("records")  #convert to list of dicts
            return relations_dict
        else:
            print(f"No {type} relations found in {clean_csv}.")
            return []
        
        