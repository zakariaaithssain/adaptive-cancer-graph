import pandas as pd

from neo4j import GraphDatabase

from config.neo4jdb_config import NEO4J_AUTH, NEO4J_URI



class Neo4jAuraConnector: 
    def __init__(self):
        self.driver = GraphDatabase.driver(
                                            uri=NEO4J_URI,
                                            auth=NEO4J_AUTH, 
                                            database= None
                                            )

#there are many ways to do so: 
# UNWIND: load csvs to pandas -> to list of dicts -> load them as batches
#this is not memory efficient because of loops nor network efficient (1 transaction/batch)

#LOAD CSV: we can load the whole csv, this is efficient for large files.
# and there are two options: 
#- we configure neo4j's import folder path or put the csv there
#this is only possible using a local instance, but we are using Aura cloud.
#- serve the csv to it using HTTP, I will use github for this. 
 
    def load_ents_to_neo4j(self, server_url): 

        with self.driver as driver: 
            driver.execute_query(
query_= 
        "LOAD CSV WITH HEADERS FROM $server AS entity"
        "MERGE (e: entity.:LABEL {'id': entity.:ID, 'cui': entity.cui, 'normalized_name': entity.normalized_name, 'normalization_source': entity.normalization_source, 'url': entity.url})"
        "SET e.name = entity.name"
        "USING PERIODIC COMMIT 1000"
        ,

parameters_={"server" : server_url}
            )

        return self #in case I want to chain methods
    
    def load_rel_to_neo4j(self, server_url): 
        with self.driver as driver: 
            driver.execute_query(
query_= "LOAD CSV WITH HEADERS FROM $server AS relation"
        "MATCH (start: {'id': relation.:START_ID})"
        "MATCH (end: {'id': relation.:END_ID})"
        "MERGE (start)-[:relation.:TYPE {'pmid': relation.mpid, 'pmcid': relation.pmcid}]->(end)"
        "USING PERIODIC COMMIT 1000"
        ,
parameters_= {"server":server_url}
            )
        return self

        

        