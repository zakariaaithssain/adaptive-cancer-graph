""""this will contain helper functions for the project"""

import logging

from config.apis_config import QUERIES


def get_data_from_apis(pubmed_api, pubmedcentral_api, extract_abstracts_only, max_results = 10000): 
        all_articles = []
        pmc_prost_articles = 0
        pmc_stomach_articles = 0 
        
        for cancer in QUERIES.keys(): 
            logging.info(f"Connector: Working On: {cancer} cancer.\n") 

            search_results = pubmed_api.search(QUERIES[cancer], max_results=max_results)
            search_results_count = pubmed_api.search_results_count
            start = 0
            while search_results_count:
                print("while loop: ", search_results_count)
                fetched_xml = pubmed_api.fetch(search_results, start=start, max_results=max_results)
                articles = pubmed_api.get_data_from_xml(fetched_xml)
                all_articles.extend(articles)

                #only get the full article body if required.
                if not extract_abstracts_only: 
                    for article in articles: 
                        #adding cancer type
                        article["cancertype"] = cancer
                        #checking if MPC id is available for the article
                        pmc_id = article["pmcid"]
                        if pmc_id: 
                            article["body"] = pubmedcentral_api.get_data_from_xml(pmc_id=pmc_id)
                            if cancer == "prostate":
                                pmc_prost_articles+=1
                            else:
                                pmc_stomach_articles +=1
                search_results_count-= max_results
                start += max_results

        logging.info(f"Helper: Prostate Cancer: {pmc_prost_articles} Articles Content Present In PubMedCentral.")
        logging.info(f"Helper: Stomach Cancer: {pmc_stomach_articles} Articles Content Present In PubMedCentral.")

        return all_articles 
