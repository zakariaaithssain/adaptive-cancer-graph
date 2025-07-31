from modules.pubmed_api import PubMedAPI
from modules.pubmedcentral_api import PubMedCentralAPI
from config.apiconfig import API_KEY_EMAIL, QUERIES


pubmed_api = PubMedAPI(api_key = API_KEY_EMAIL["api_key"], email = API_KEY_EMAIL["email"])
pubmedcentral_api = PubMedCentralAPI(api_key = API_KEY_EMAIL["api_key"], email = API_KEY_EMAIL["email"])

all_articles = {}
prostate_pmc = 0
stomach_pmc = 0 
for cancer in QUERIES.keys():  
    fetched_xml = pubmed_api.search_and_fetch(QUERIES[cancer], max_results=1000)
    articles = pubmed_api.get_data_from_xml(fetched_xml)
    all_articles[cancer] = articles
    for article in articles: 
        pmc_id = article["pmcid"]
        if pmc_id: 
            if cancer == "prostate": prostate_pmc+=1
            else: stomach_pmc +=1
            print(pmc_id)
            article["body"] = pubmedcentral_api.get_data_from_xml(pmc_id=pmc_id)

print("pmc ids for prostate: ", prostate_pmc)
print("pmc id for stomach: ", stomach_pmc)


    







