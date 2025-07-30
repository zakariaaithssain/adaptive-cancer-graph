from modules.pubmed_api import PubMedAPI
from config.apiconfig import API_KEY_EMAIL, QUERIES


pubmed_api = PubMedAPI(api_key = API_KEY_EMAIL["api_key"], email = API_KEY_EMAIL["email"])

all_articles = {}
available_pmcid = 0
for cancer in QUERIES.keys():  
    articles = pubmed_api.search_and_fetch(QUERIES[cancer], max_results=1000)
    all_articles[cancer] = articles
    for article in articles: 
        if article["pmcid"]: 
            print(article["pmcid"])
            available_pmcid+=1

print("available PubMed Central Id in 1000*number_of_cancers articles: ", available_pmcid)
    







