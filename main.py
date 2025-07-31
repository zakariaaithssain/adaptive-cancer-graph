import logging 

from modules.pubmed_api import PubMedAPI
from modules.pubmedcentral_api import PubMedCentralAPI
from modules.apis_to_mongo import APIsToMongo

from config.apis_config import API_KEY_EMAIL

from config.log_config import LOG_OPTIONS



logging.basicConfig(level=LOG_OPTIONS["level"], format=LOG_OPTIONS["format"],
                handlers=[
                            logging.FileHandler(LOG_OPTIONS["file_handler"], mode= LOG_OPTIONS["mode"]),

                            logging.StreamHandler()  # shows logs in terminal
                            ]
                )


pubmed_api = PubMedAPI(api_key = API_KEY_EMAIL["api_key"], email = API_KEY_EMAIL["email"])
pubmedcentral_api = PubMedCentralAPI(api_key = API_KEY_EMAIL["api_key"], email = API_KEY_EMAIL["email"])

connector = APIsToMongo(pubmed_api=pubmed_api, pubmedcentral_api=pubmedcentral_api)

connector.get_docs_from_apis(max_results=1000).insert_docs_to_mongo() #chaining thanks to returning self.