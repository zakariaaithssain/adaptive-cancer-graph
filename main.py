import logging 

from modules.pubmed_api import PubMedAPI
from modules.pubmedcentral_api import PubMedCentralAPI
from modules.mongo_connector import MongoAtlasConnector
from functions.helpers import get_data_from_apis

from config.apis_config import API_KEY_EMAIL


pubmed_api = PubMedAPI(api_key = API_KEY_EMAIL["api_key"], email = API_KEY_EMAIL["email"])
pubmedcentral_api = PubMedCentralAPI(api_key = API_KEY_EMAIL["api_key"], email = API_KEY_EMAIL["email"])

#use_abstract_only = False means that we are getting also articles body if available. 
connector = MongoAtlasConnector(pubmed_api=pubmed_api, pubmedcentral_api=pubmedcentral_api, extract_abstracts_only=False)
try: 
    all_articles = get_data_from_apis(pubmed_api, pubmedcentral_api, extract_abstracts_only=False, max_results=10000)
    connector.load_to_cloud(all_articles)

except KeyboardInterrupt: 
    logging.error("Main: Process Interrupted Manually.")