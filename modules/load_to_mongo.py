from pymongo import MongoClient
from pymongo import errors
from pymongo.server_api import ServerApi
from datetime import datetime
from tqdm import tqdm

import logging
import datetime
import sys


from config.apis_config import QUERIES
from config.mongodb_config import CONNECTION_STR, DB_STRUCTURE


"""
    a cluster contains multiple databases, a database contains multiple collections,
    a collection contains multiple docs, a doc contains multiple features.
    """

class APIsToMongo:
    def __init__(self,pubmed_api, pubmedcentral_api, use_abstracts_only = True):
        self.use_abstracts_only = use_abstracts_only
        self.pubmed_api = pubmed_api
        #if we wanna get also the articles body, set to False
        if not self.use_abstracts_only: self.pubmedcentral_api = pubmedcentral_api

        #create a new client and connect to the server
        self.cluster = MongoClient(host= CONNECTION_STR, server_api=ServerApi('1'))

        #send a ping to confirm a successful connection
        try:
            logging.info("Connector: Sending A Ping To Confirm Connection.")
            self.cluster.admin.command('ping')
            logging.info("Connector: Deployment Pinged. Successfully Connected To MongoDB Atlas.")
        except Exception as e:
            logging.error(f"Connector: Error: {e}")
            sys.exit(1)


        self.db = self.cluster["fetched-data-db"]
        self.collection = self.db["pm-pmc-data"]

        logging.info(f"Connector: Cluster: {DB_STRUCTURE['cluster']}.")
        logging.info(f"Connector: DataBase: {DB_STRUCTURE['database']}.")
        logging.info(f"Connector: Collection: {DB_STRUCTURE['collection']}.")

        # using 'pmid' to prevent duplicates
        self.collection.create_index("pmid", unique=True)
        logging.info("Connector: Using 'pmid' As An Index.\n")

        self.all_articles = []
        self.pmc_prost_articles = 0
        self.pmc_stomach_articles = 0 




    def get_docs_from_apis(self, max_results = 1000, ): 
        for cancer in QUERIES.keys(): 
            logging.info(f"Connector: Working On: {cancer} cancer.\n") 

            fetched_xml = self.pubmed_api.search_and_fetch(QUERIES[cancer], max_results=max_results)
            articles = self.pubmed_api.get_data_from_xml(fetched_xml)

            self.all_articles.extend(articles)
            for article in articles: 
                #adding cancer type
                article["cancertype"] = cancer

                #checking if MPC id is available for the article
                
                pmc_id = article["pmcid"]
                if not self.use_abstracts_only: #only get the full article body if required.
                    if pmc_id: 
                        article["body"] = self.pubmedcentral_api.get_data_from_xml(pmc_id=pmc_id)

                        if cancer == "prostate":
                            self.pmc_prost_articles+=1
                        else:
                            self.pmc_stomach_articles +=1

        logging.info(f"Connector: Prostate Cancer: {self.pmc_prost_articles} Articles Content Present In PubMedCentral.")
        logging.info(f"Connector: Stomach Cancer: {self.pmc_stomach_articles} Articles Content Present In PubMedCentral.")

        return self #to be able to chain call methods 



    def insert_docs_to_mongo(self):
        logging.info("Connector: Inserting New Docs. Already Present Ones Will Be Ignored.")
        for article in tqdm(self.all_articles):
            try:
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

        







