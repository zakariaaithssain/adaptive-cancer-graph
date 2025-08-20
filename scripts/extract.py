""""this will contain Extraction Process functions for the project"""
import logging 
import pickle
from tqdm import tqdm

from modules.pubmed_api import PubMedAPI
from modules.pubmedcentral_api import PubMedCentralAPI
from modules.mongoatlas import MongoAtlasConnector

from config.apis_config import PM_API_KEY_EMAIL
from config.apis_config import PM_QUERIES
from config.mongodb_config import CONNECTION_STR



#api key and email are optional, but if not provided, we have less requests rate. 
pubmed_api = PubMedAPI(api_key = PM_API_KEY_EMAIL["api_key"],
                        email = PM_API_KEY_EMAIL["email"])

pubmedcentral_api = PubMedCentralAPI(api_key = PM_API_KEY_EMAIL["api_key"],
                                        email = PM_API_KEY_EMAIL["email"])

mongo_connector = MongoAtlasConnector(connection_str=CONNECTION_STR)


#less max_results, less API pression, more loop iterations
#if max results is not specified, the default is 1k, the max is 10k
def extract_pubmed_to_mongo(extract_abstracts_only=True, max_results=1000):
    try: 
        all_articles = _get_data_from_apis(pubmed_api, pubmedcentral_api,
                                        extract_abstracts_only,
                                            max_results) 
        
        mongo_connector.load_articles_to_atlas(all_articles, abstract_only = True)

    except KeyboardInterrupt: 
        logging.error("Extraction Process Interrupted Manually.")
        raise




def _get_data_from_apis(pubmed_api:PubMedAPI, pubmedcentral_api:PubMedCentralAPI, extract_abstracts_only = True, max_per_query = 1000, max_per_call = 1000): 
        """ 
        #arguments:
                pubmed_api (resp. pubmedcentral_api) = PubMedAPI (resp. PubMedCentralAPI) instance 
                extract_abstracts_only = when set to False, it extracts also articles body.
                                        This takes time because it requires an API call per article.
                max_per_call = the number of articles to get per API call.
                #Note = the code is designed to always get all articles available per query, so 
                the max_results is only for specifiying how much to request from the API per iteration. 
                Decreasing max_results increases the number of loop iterations, but inhances API performance.
                """
        
        all_articles = []

        if extract_abstracts_only: logging.info(f"Extraction Process: Extracting Abstracts Only. No Calls To PubMedCentral API.\n")
        else: logging.info(f"Extraction Process: Extracting Abstracts And Body. PubMedCentral API Will Be Called For Each Article.\n")
        
        for query in PM_QUERIES.keys():
            logging.info(f"Extraction Process: Working On: {query.capitalize()} Query.\n")

            # searching only once, and using pagination to get all articles per search
            search_results = pubmed_api.search(PM_QUERIES[query], max_results=max_per_call) #a json format
            total_count = pubmed_api.search_results_count
            start = 0
            
            # checking the API's hard limit (10k articles per query)

            print(f"Extracting articles for {query}query...")
            while start < total_count and start < max_per_query:  
                remaining = min(total_count - start, max_per_query - start) 
                current_max = min(max_per_call, remaining)
                logging.info(f"Extraction Process: {remaining} Articles To Get.")

                current_max = min(max_per_call, remaining)
                fetched_xml = pubmed_api.fetch(search_results, start=start, max_results=current_max)
                articles = pubmed_api.get_data_from_xml(fetched_xml)
                all_articles.extend(articles)

                # get full body if specified
                if not extract_abstracts_only:
                    for article in articles:
                        pmc_id = article["pmcid"]
                        if pmc_id and pmc_id not in pubmedcentral_api.pmcids_cache:
                            pubmedcentral_api.pmcids_cache.add(pmc_id)
                            article["body"] = pubmedcentral_api.get_data_from_xml(pmc_id=pmc_id)

                    pubmedcentral_api._save_cache()        
                start += max_per_call
            
        else: logging.info(f"Extraction Process: Finished Collecting Articles Abstracts.")

        return all_articles 

