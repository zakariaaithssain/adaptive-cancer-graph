from pymongo import MongoClient
from pymongo import errors
from pymongo.server_api import ServerApi

from datetime import datetime

from config.apis_config import QUERIES
from config.mongodb_config import CONNECTION_STR

"""
    a cluster contains multiple databases, a database contains multiple collections,
    a collection contains multiple docs, a doc contains multiple features.
    """

class APIsToMongo:
    def __init__(self,pubmed_api, pubmedcentral_api):
        
        self.pubmed_api = pubmed_api
        self.pubmedcentral_api = pubmedcentral_api

        #create a new client and connect to the server
        self.cluster = MongoClient(host= CONNECTION_STR, server_api=ServerApi('1'))

        #send a ping to confirm a successful connection
        try:
            self.cluster.admin.command('ping')
            print("Pinged your deployment. Successfully connected to MongoDB.")
        except Exception as e:
            print(e)

        self.db = self.cluster["fetched-data-db"]
        self.collection = self.db["pm-pmc-data"]
        # using 'pmid' to prevent duplicates
        self.collection.create_index("pmid", unique=True)

        self.all_articles = []
        self.pmc_prost_articles = 0
        self.pmc_stomach_articles = 0 




    def get_docs_from_apis(self, max_results = 1000): 
        
        print("fetching...")
        for cancer in QUERIES.keys():  
            fetched_xml = self.pubmed_api.search_and_fetch(QUERIES[cancer], max_results=max_results)
            articles = self.pubmed_api.get_data_from_xml(fetched_xml)

            self.all_articles.extend(articles)
            for article in articles: 
                #adding cancer type
                article["cancertype"] = cancer

                #checking if MPC id is available for the article
                
                pmc_id = article["pmcid"]
                if pmc_id: 
                    article["body"] = self.pubmedcentral_api.get_data_from_xml(pmc_id=pmc_id)

                    if cancer == "prostate":
                        self.pmc_prost_articles+=1
                    else:
                        self.pmc_stomach_articles +=1

        print("pmc ids for prostate: ", self.pmc_prost_articles)
        print("pmc id for stomach: ", self.pmc_stomach_articles)

        return self #to be able to chain call methods 



    def insert_docs_to_mongo(self):
        for article in self.all_articles:
            try:
                # adding the date of fetching the article
                article["fetchingdate"] = datetime.now(datetime.timezone.utc)

                self.collection.update_one(
                    {"pmid": article["pmid"]},     # matching by PubMed id
                    {"$setOnInsert": article},     # insert only if not already present
                    upsert=True
                )
            except errors.PyMongoError as e:
                print(f"error inserting article with PMID {article.get('pmid')}: {e}")
        else: 
            print(f"{len(self.all_articles)} (counting also already existing ones) docs inserted successfully.")

        







