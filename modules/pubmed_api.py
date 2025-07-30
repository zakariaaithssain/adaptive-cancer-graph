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
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json',
            'usehistory': 'y'
        }
        
        if self.api_key:
            search_params['api_key'] = self.api_key
        if self.email:
            search_params['email'] = self.email
            
        response = rq.get(search_url, params=search_params)
        
        if self.api_key: API_SLEEP_TIME["with_key"]   #with an api key, we are allowed to do 10req/second
        else: API_SLEEP_TIME["without_key"]           #without an api key, we only have 3req/second 
        
        search_data = response.json()
        
        # Step 2: Fetch abstracts using history
        fetch_url = f"{self.base_url}efetch.fcgi"
        fetch_params = {
            'db': 'pubmed',
            'WebEnv': search_data['esearchresult']['webenv'],
            'query_key': search_data['esearchresult']['querykey'],
            'retmode': 'xml',
            'rettype': 'abstract',
            'retmax': max_results
        }
        
        if self.api_key:
            fetch_params['api_key'] = self.api_key
            
        fetch_response = rq.get(fetch_url, params=fetch_params)
        time.sleep(0.34)
        
        return self.parse_abstracts(fetch_response.text)
    
    def parse_abstracts(self, xml_text):
        root = ET.fromstring(xml_text)
        articles = []
        
        for article in root.findall('.//PubmedArticle'):
            title_elem = article.find('.//ArticleTitle')
            abstract_elem = article.find('.//AbstractText')
            pmid_elem = article.find('.//PMID')
            
            # get MeSH terms (medical subject headings for additional entities or labels in neo4j)
            mesh_terms = []
            for mesh in article.findall('.//MeshHeading/DescriptorName'):
                mesh_terms.append(mesh.text)
            
            # get keywords for more entities 
            keywords = []
            for keyword in article.findall('.//Keyword'):
                keywords.append(keyword.text)
                
            articles.append({
                'pmid': pmid_elem.text if pmid_elem is not None else None,
                'title': title_elem.text if title_elem is not None else None,
                'abstract': abstract_elem.text if abstract_elem is not None else None,
                'mesh_terms': mesh_terms,  # curated medical terms
                'keywords': keywords       # keywords provided by author
            })
        
        return articles



