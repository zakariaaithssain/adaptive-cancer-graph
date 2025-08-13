""""this will contain helper functions for the project"""

import logging

from config.apis_config import QUERIES


def get_data_from_apis(pubmed_api, pubmedcentral_api, extract_abstracts_only = True, max_results = 1000): 
        """ 
        #arguments:
                pubmed_api (resp. pubmedcentral_api) = PubMedAPI (resp. PubMedCentralAPI) instance 
                extract_abstracts_only = when set to False, it extracts also articles body.
                                        This takes time because it requires an API call per article.
                max_results = the number of articles to get per iteration.
                #Note = the code is designed to always get all the articles available per query, so 
                the max_results is only for specifiying what to request from the API per iteration. 
                Decreasing max_results increases the number of loop iterations and of PubMed Efetch API endpoint calls
                """
        
        all_articles = []
        pmc_prost_articles = 0
        pmc_stomach_articles = 0 
        
        for cancer in QUERIES.keys():
            logging.info(f"Helper: Working On: {cancer.capitalize()} Cancer.\n")

            # searching only once, and using pagination to get all articles per search
            search_results = pubmed_api.search(QUERIES[cancer], max_results=max_results) #a json format
            total_count = pubmed_api.search_results_count
            start = 0

            while start < total_count: #to get all the articles returned from query
                logging.info(f"Helper: {total_count - start} Articles To Get.")
                fetched_xml = pubmed_api.fetch(search_results, start=start, max_results=max_results)
                articles = pubmed_api.get_data_from_xml(fetched_xml)
                all_articles.extend(articles)

                # get full body if specified
                if not extract_abstracts_only:
                    for article in articles:
                        article["cancertype"] = cancer
                        pmc_id = article["pmcid"]
                        if pmc_id:
                            article["body"] = pubmedcentral_api.get_data_from_xml(pmc_id=pmc_id)
                            if cancer == "prostate":
                                pmc_prost_articles += 1
                            else:
                                pmc_stomach_articles += 1

                start += max_results



        logging.info(f"Helper: Prostate Cancer: {pmc_prost_articles} Articles Content Present In PubMedCentral.")
        logging.info(f"Helper: Stomach Cancer: {pmc_stomach_articles} Articles Content Present In PubMedCentral.")

        return all_articles 
