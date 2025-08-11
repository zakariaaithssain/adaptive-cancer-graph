import logging 

from modules.pubmed_api import PubMedAPI
from modules.pubmedcentral_api import PubMedCentralAPI
from modules.load_to_mongo import APIsToMongo

from config.apis_config import API_KEY_EMAIL


pubmed_api = PubMedAPI(api_key = API_KEY_EMAIL["api_key"], email = API_KEY_EMAIL["email"])
pubmedcentral_api = PubMedCentralAPI(api_key = API_KEY_EMAIL["api_key"], email = API_KEY_EMAIL["email"])

connector = APIsToMongo(pubmed_api=pubmed_api, pubmedcentral_api=pubmedcentral_api)
try: 
    #we can chain thanks to returning self from the 1st method. 
    connector.get_docs_from_apis(max_results=1000).insert_docs_to_mongo() 

except KeyboardInterrupt: 
    logging.error("Main: Process Interrupted Manually.")