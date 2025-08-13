from pymongo import MongoClient
from pymongo import errors
from pymongo.server_api import ServerApi
from datetime import datetime
from tqdm import tqdm

import logging
import datetime
import sys

from config.mongodb_config import CONNECTION_STR, DB_STRUCTURE



#TODO: ADD A METHOD THAT GETS ALL ARTICLES FROM MONGO TO BE PROCESSED USING NLP
#TODO 2: IF I WILL STORE THE ENTITIES AND RELATIONS IN MONGO, IMPLEMENT A METHOD TO LOAD THEM TO CLOUD.
# BUT I THINK IT'S BETTER TO STORE THEM AS TABULAR DATA OR IN CSV THEN TO NEO4J.
"""
    a cluster contains multiple databases, a database contains multiple collections,
    a collection contains multiple docs, a doc contains multiple features.
    """

class MongoAtlasConnector:
    def __init__(self):
        #create a new client and connect to the server
        self.cluster = MongoClient(host= CONNECTION_STR, server_api=ServerApi('1'))

        #send a ping to confirm a successful connection
        try:
            logging.info("Connector: Sending A Ping To Confirm Connection.")
            self.cluster.admin.command('ping')
            logging.info("Connector: Deployment Pinged. Successfully Connected To MongoDB Atlas.")
        except Exception as e:
            logging.error(f"Connector: Error: {e}")
            #no need to continue the execution if connection failed
            sys.exit(1)


        self.db = self.cluster[DB_STRUCTURE['database']]
        self.collection = self.db[DB_STRUCTURE['collection']]

        logging.info(f"Connector: Cluster: {DB_STRUCTURE['cluster']}.")
        logging.info(f"Connector: DataBase: {DB_STRUCTURE['database']}.")
        logging.info(f"Connector: Collection: {DB_STRUCTURE['collection']}.")

        # using 'pmid' to prevent duplicates
        self.collection.create_index("pmid", unique=True)
        logging.info("Connector: Using 'pmid' As An Index.\n")

        


    def load_articles_to_cloud(self, all_articles, abstract_only = True):
        logging.info("Connector: Inserting New Docs. Already Present Ones Will Be Ignored.")
        for article in tqdm(all_articles):
            try:
                if article['abstract']: #ignoring empty articles.
                    # adding the date of fetching the article (utc: coordinated universal time)
                    article["fetchingdate"] = datetime.datetime.now(datetime.timezone.utc) 
                    self.collection.update_one(
                        {"pmid": article["pmid"]},     # matching by PubMed id
                        {"$setOnInsert": article},   
                        upsert=True                    #insert if no doc with that pmid is already there
                    )
            except errors.PyMongoError as e:
                logging.error(f"Connector: Article PMid: {article.get('pmid')}: Error: {e}.")
        else: 
            logging.info("Connector: Data Inserted With No Errors.")

        







