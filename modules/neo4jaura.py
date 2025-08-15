import pandas as pd

from neo4j import GraphDatabase

import os 
import shutil

from config.neo4jdb_config import NEO4J_LABELS, NEO4J_REL_TYPES

"""to load data to neo4j, we have multiple options:
    1 - load every entity or relation independently from others. 
    pros: allows dynamic labels and relations types.
    cons: not memory efficient (loops) nor network efficient 
          (1entity or relation/transaction
    2 - use CYPHER methods (either UNWIND or LOAD CSV)
    pros: memory efficient (UNWIND loads a batch, LOAD CSV loads an intire csv at once)
          network efficient (UNWIND: a batch in one connection, LOAD CSV I think the 
          whole csv in one connection)
    cons: uses plain cypher so no formatting is possible for dynamic labels 
    and relations types. this can be fixed via APOC if I am using local instance
    of Neo4j, but using it can make CI/CD hard. 
    3 - I want dynamic labels and relation types, and I want efficiency, 
    so I will create a separate csv for each entity type (especially that I already
    know the entities that the model can recognize!!!!) then use LOAD CSV. 
     (but I need somewhere to host those files)
      Or I can use UNWIND, but it will be a lil memory unefficient """



NEO4J_LABELS = ['AMINO_ACID',
                'ANATOMICAL_SYSTEM',
                'CANCER',
                'CELL',
                'CELLULAR_COMPONENT',
                'DEVELOPING_ANATOMICAL_STRUCTURE',
                'GENE_OR_GENE_PRODUCT',
                'IMMATERIAL_ANATOMICAL_ENTITY',
                'MULTI_TISSUE_STRUCTURE',
                'ORGAN',
                'ORGANISM',
                'ORGANISM_SUBDIVISION',
                'ORGANISM_SUBSTANCE',
                'PATHOLOGICAL_FORMATION',
                'SIMPLE_CHEMICAL',
                'TISSUE']

#relations we defined in config/nlp_config
NEO4J_REL_TYPES = ['PRODUCES',
                   'CONTAINS',
                   'BINDS',
                   'REGULATES',
                   'EXPRESSED_IN',
                   'MUTATED_IN',
                   'PART_OF',
                   'LOCATED_IN',
                   'ORIGIN_OF',
                   'CONTAINS_COMPONENT',
                   'SURROUNDS',
                   'DEVELOPS_INTO',
                   'ORIGINATES_FROM',
                   'ARISES_FROM',
                   'AFFECTS',
                   'ASSOCIATED_WITH',
                   'DAMAGES',
                   'BIOMARKER_FOR',
                   'TOXIC_TO',
                   'COMPONENT_OF',
                   'SECRETED_BY',
                   'TREATS']

import pandas as pd
from neo4j import GraphDatabase
from typing import List, Dict

class Neo4jAuraConnector:
    def __init__(self, uri: str, auth: tuple):
        self.driver = GraphDatabase.driver(uri, auth=auth)

    def _batch_load(self, data: List[Dict], label: str, batch_size: int = 1000):
        """Batch load using UNWIND for optimal performance"""
        with self.driver.session() as session:
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                query = f"""
                UNWIND $batch AS row
                MERGE (n:{label} {{id: row.id}})
                SET n += row
                """
                session.run(query, batch=batch)

    def GENE_to_neo4j(self, csv_path: str):
        """Load GENE data from CSV without file hosting"""
        # Read and preprocess data
        df = pd.read_csv(csv_path)
        genes = df[df[":LABEL"] == "GENE"].copy()
        
        # Format for Neo4j
        genes.rename(columns={":ID": "id"}, inplace=True)
        genes.drop(columns=[":LABEL"], inplace=True)
        genes_dict = genes.to_dict("records")  # Convert to list of dicts
        
        # Batch load
        self._batch_load(genes_dict, "GENE")
        print(f"Loaded {len(genes_dict)} GENE nodes")
        return self

    def close(self):
        self.driver.close()

# Usage Example
if __name__ == "__main__":
    loader = Neo4jAuraConnector(
        uri="neo4j+s://your-aura-instance.databases.neo4j.io",
        auth=("neo4j", "your-password")
    )
    loader.GENE_to_neo4j("your_data.csv").close()