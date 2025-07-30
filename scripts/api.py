from modules.pubmed_api import PubMedAPI
from config.apiconfig import API_KEY_EMAIL, QUERIES


pubmed_api = PubMedAPI(api_key = API_KEY_EMAIL["api_key"], email = API_KEY_EMAIL["email"])




all_articles = {}

for cancer in QUERIES.keys():  
    articles = pubmed_api.search_and_fetch(QUERIES[cancer], max_results=1000)
    all_articles[cancer] = articles
    print(cancer, ":", len(all_articles[cancer]))







