from modules.pubmed_api import PubMedAPI
from config.apiconfig import API_KEY_EMAIL

api = PubMedAPI(api_key = API_KEY_EMAIL["api_key"], email = API_KEY_EMAIL["email"])


queries = [
    "stomach cancer mutations genes",
    "prostate cancer risk factors treatment", 
    "gastric adenocarcinoma molecular pathways",
    "prostate cancer therapy resistance"
]

all_articles = []
for query in queries:
    articles = api.search_and_fetch(query, max_results=500)
    all_articles.extend(articles)
    print(f"Retrieved {len(articles)} articles for: {query}")


