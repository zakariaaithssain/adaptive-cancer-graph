import requests as rq
import xml.etree.ElementTree as ET

import time

from config.apiconfig import API_SLEEP_TIME


class PubMedAPI:
    def __init__(self, api_key=None, email=None):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.api_key = api_key
        self.email = email
    

    
    def search_and_fetch(self, query, max_results=1000):
        
        # Step 1: Search
        search_url = f"{self.base_url}esearch.fcgi"
        search_params = {
            'db': 'pubmed', #database
            'term': query, #the query like the one we write in the search bar
            'retmax': max_results, #ret: return
            'retmode': 'json', #json is available as a return type for search endpoint
            'usehistory': 'y' #whether to use the history or not
        }
        
        if self.api_key:
            search_params['api_key'] = self.api_key
        if self.email:
            search_params['email'] = self.email
            
        search_response = rq.get(search_url, params=search_params)
        
        if self.api_key: 
            time.sleep(API_SLEEP_TIME["with_key"])    #with an api key, we are allowed to do 10req/second
        else: 
            time.sleep(API_SLEEP_TIME["without_key"]) #without an api key, we only have 3req/second 
        
        search_data = search_response.json()
        
        # Step 2: Fetch abstracts using history
        fetch_url = f"{self.base_url}efetch.fcgi"
        fetch_params = {
            'db': 'pubmed',
            'WebEnv': search_data['esearchresult']['webenv'],
            'query_key': search_data['esearchresult']['querykey'],
            'retmode': 'xml', #json is not available for fetching endpoint
            'rettype': 'abstract',
            'retmax': max_results
        }
        
        if self.api_key:
            fetch_params['api_key'] = self.api_key
            
        fetch_response = rq.get(fetch_url, params=fetch_params)
        if self.api_key: 
            time.sleep(API_SLEEP_TIME["with_key"])  
        else: 
            time.sleep(API_SLEEP_TIME["without_key"])   
        
        return self.parse_metadata_from_xml(fetch_response)
    

    
    def parse_metadata_from_xml(self, xml):
        root = ET.fromstring(xml.text)
        articles = [] 
        
        for article in root.findall('.//PubmedArticle'):
            article_title = article.find('.//ArticleTitle')
            article_abstract = article.find('.//AbstractText')
            article_pmid = article.find('.//PMID') #PubMed id of the article

            article_pmcid = None #PubMed Central id of the article (it is available only when the articles body is available for free)
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

                'pmcid': article_pmcid.text.replace("PMC", "") if article_pmcid is not None else None,

                'title': article_title.text if article_title is not None else None,

                'abstract': article_abstract.text if article_abstract is not None else None,

                'medical_subject_headings': medical_subject_headings ,  # curated medical terms

                'keywords': keywords       # keywords provided by author
            })
        
        return articles #list of dicts, each dict is an article's metadata containing the keys above.



