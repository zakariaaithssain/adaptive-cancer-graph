import requests as rq
import xml.etree.ElementTree as ET

import time

from config.apis_config import API_SLEEP_TIME


class PubMedAPI:
    def __init__(self, api_key=None, email=None):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.api_key = api_key
        self.email = email
        self.headers = { "User-Agent": "MyResearchBot/1.0 (zakaria04aithssain@gmail.com)" }
    

    
    def search_and_fetch(self, query = None, max_results=1000, db = "pubmed", pmc_id = None, rettype = 'abstract'): 
        """ 
        for PubMed Central API:
                db = 'pmc'
                pmc_id = string pmc id without the PMC prefixe
                rettype = 'full' 

                """
        
        # step1: search, only when using the pubmed API, not for PMC API (we already have an id)
        if pmc_id is None: #which means that we are using the PubMed API
            search_url = f"{self.base_url}esearch.fcgi"
            search_params = {
                'db': db,              #database
                'term': query,         #the query like the one we write in the search bar
                'retmax': max_results, #ret: return
                'retmode': 'json',     #json is available as a return type for search endpoint
                'usehistory': 'y'      #whether to use the history or not
            }
            if self.api_key:
                search_params['api_key'] = self.api_key
            if self.email:
                search_params['email'] = self.email
            
            search_response = rq.get(search_url, params=search_params, headers=self.headers)
                
            if self.api_key: 
                time.sleep(API_SLEEP_TIME["with_key"])    #with an api key, we are allowed to do 10req/second
            else: 
                time.sleep(API_SLEEP_TIME["without_key"]) #without an api key, we only have 3req/second 
            
            search_data = search_response.json()
        
        # step2: fetching (either using history if PubMed API, or using mpc_id if PubMedCentral API) 
        fetch_url = f"{self.base_url}efetch.fcgi"
        fetch_params = {
            'db': db,
            'retmode': 'xml',   #json is not available for fetch endpoint
            'rettype': rettype, #"abstract" if PubMed else "full"
        }

        #adding history params and max results only if dealing with PubMed API 
        if pmc_id is None: #which means that we are using PubMed API, we already have the search_data.
            fetch_params['WebEnv'] = search_data['esearchresult']['webenv']
            fetch_params['query_key'] = search_data['esearchresult']['querykey']
            fetch_params['retmax'] = max_results
        else:              #which means that we are using PMC API, we have an id. 
            fetch_params['id'] = pmc_id 

        if self.api_key:
            fetch_params['api_key'] = self.api_key
        if self.email:
            fetch_params['email'] = self.email
        
            
        fetch_response = rq.get(fetch_url, params=fetch_params, headers=self.headers)
        if self.api_key: 
            time.sleep(API_SLEEP_TIME["with_key"])  
        else: 
            time.sleep(API_SLEEP_TIME["without_key"])   
        
        return fetch_response #xml that contains the data of searched articles
                              #(resp. article with pmc_id)
                              # if we are using PM API (resp. PMC API)
    

    
    def get_data_from_xml(self, fetch_response): #this is only for the PubMed API, I @override it for MPC API. 
        root = ET.fromstring(fetch_response.text)
        articles = [] 
        
        for article in root.findall('.//PubmedArticle'):
            article_title = article.find('.//ArticleTitle')
            article_abstract = article.find('.//AbstractText')
            article_pmid = article.find('.//PMID') #PubMed id of the article
#PubMed Central id of the article (it is available only when the articles body is available for free)
            article_pmcid = None 
            for article_id in article.findall('.//ArticleId'):
                id_type = article_id.get('IdType')
                if id_type == 'pmc':
                    article_pmcid = article_id
                if article_pmcid: break
            
            # get mesh terms (medical subject headings for additional entities or labels in neo4j)
            medical_subject_headings  = []
            for mesh in article.findall('.//MeshHeading/DescriptorName'):
                medical_subject_headings.append(mesh.text)
            
            # get keywords for more entities 
            keywords = []
            for keyword in article.findall('.//Keyword'):
                keywords.append(keyword.text)
                
            articles.append({

                'pmid': article_pmid.text if article_pmid is not None else None, 
                #remove the PMC prefixe from the pmc ids.
                'pmcid': article_pmcid.text.replace("PMC", "") if article_pmcid is not None else None,

                'title': article_title.text if article_title is not None else None,

                'abstract': article_abstract.text if article_abstract is not None else None,

                'medical_subject_headings': medical_subject_headings ,  # curated medical terms

                'keywords': keywords       # keywords provided by author
            })
        
        return articles #list of dicts, each dict is an article's metadata containing the keys above.



