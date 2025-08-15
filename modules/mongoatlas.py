from pymongo import MongoClient
from pymongo import errors
from pymongo.server_api import ServerApi
from datetime import datetime
from tqdm import tqdm

import logging
import datetime
import sys

from config.mongodb_config import CONNECTION_STR, DB_STRUCTURE


#TODO: clean the database from old data before running the fetching script
#TODO: add logic to load_articles_to_cloud that verifies also that the body
#  is not None before inserting to cloud

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

        


    def load_articles_to_atlas(self, all_articles, abstract_only = True):
        logging.info("Connector: Inserting New Docs. Already Present Ones Will Be Ignored.")
        print("inserting new docs, present and empty ones are ignored...")
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
                logging.error(f"Connector: Unable To Store Article PMID{article.get('pmid')}: {e}.")
        else: 
            logging.info("Connector: Data Inserted With No Errors.")


    
    def fetch_articles_from_atlas(self, query = {}):
        """
        query = {} to fetch all data.

        """
        articles = []
        try: 
            cursor = self.collection.find(query) #it returns a cursor, we must iterate through it.
        except errors.PyMongoError as e: 
            logging.error(f"Connector: Unable To Fetch Docs: {e}.")
        logging.info("Connector: Fetching Docs From Mongo Atlas...")
        print("fetching docs...")
        for doc in tqdm(cursor):
            try:
                if isinstance(doc['abstract'], str) or ('body' in doc.keys() and isinstance(doc['body'], str)):
                    article = {}

                    article['pmid'] = doc['pmid']
                    article['pmcid'] = doc['pmid'] #will be null if article not available in MPCentral.
                    article['fetching_date'] = doc['fetchingdate']

                    texts = []
                    #add keywords and MeSH to texts.
                    keywords = [elt for elt in doc['keywords'] if isinstance(elt, str)]
                    mesh = [elt for elt in doc['medical_subject_headings'] if isinstance(elt, str)]
                    texts.extend(mesh)
                    texts.extend(keywords)
                    #add abstract and title to text
                    if isinstance(doc.get('abstract'), str):
                        texts.append(doc['abstract'])
                    if isinstance(doc['title'], str): 
                        texts.append(doc['title'])
                    #add body, it can be missing if we only fetched abstracts.
                    if 'body' in doc.keys() and isinstance(doc['body'], str):
                        texts.append(doc['body']) 

                    article['text'] = " ".join(texts)

                    articles.append(article)
            except Exception as e: 
                logging.error(f"Connector: Unable To Fetch Article PMID{article.get('pmid')}: {e}.")
        else: 
            logging.info("Connector: Data Fetched With No Errors.")
        return articles
        
        
