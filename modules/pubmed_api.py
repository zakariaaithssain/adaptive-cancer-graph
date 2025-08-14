import requests as rq
import xml.etree.ElementTree as ET

import time
import logging

from config.apis_config import PM_API_SLEEP_TIME

# TODO : COMBINE THE RETSTART AND RETMAX PARAMS TO GET ALL ARTICLES AVAILABLE
#FOR THE QUERIES, AND KEEP TRACK OF MPIDS TO NOT REFETCH THE SAME ARTICLES,
#FOR THIS CONSIDER THE DATE PARAMS TO SPECIFY ONLY GETTING NEW ARTICLES. 
#TODO 2: FIND THE BEST WAY TO STORE ENTITIES AND RELATIONS, GHALIBAN CSV LI BLAN.
class PubMedAPI:
    def __init__(self, api_key=None, email=None):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.api_key = api_key
        self.email = email
        #this header is specific for POST HTTP method, consider changing it for GET method.
        self.headers = { 
    "User-Agent": "MedicalGraphBot/1.0 (zakaria04aithssain@gmail.com)",
    "Content-Type": "application/x-www-form-urlencoded"
}

        if api_key: logging.info("PubMed API: API Key Used.")
        else: logging.warning("PubMed API: API Key Absent.")

        if self.email: logging.info("PubMed API: Email Used.")
        else: logging.warning("PubMed API: Email Absent.")
    

    
    def search(self, query = None, max_results=1000, db = "pubmed", pmc_id = None, rettype = 'abstract'): 
        """ 
        for PubMed Central API:
                db = 'pmc'
                pmc_id = string pmc id without the PMC prefixe
                rettype = 'full' 

                """
        
        # step1: search, only when using the pubmed API, not for PMC API (we already have an id)
        if pmc_id is None: #which means that we are using the PubMed API
            search_url = f"{self.base_url}esearch.fcgi"
            search_post_data = {
                'db': db,              #database
                'term': query,         #the query like the one we write in the search bar
                'retmax': max_results, #ret: return
                'retmode': 'json',     #json is available as a return type for search endpoint
                'usehistory': 'y'      #whether to use the history or not
            }
            if self.api_key:
                search_post_data['api_key'] = self.api_key
            
            if self.email:
                search_post_data['email'] = self.email

            try: #get recieves params, post recieves data
                search_response = rq.post(search_url, data=search_post_data, headers=self.headers)
                response_code = search_response.status_code
                if response_code == 200:
                    logging.info(f"PubMed API: Search Endpoint: Response OK: {response_code}")
                    
                    #to get the number of results the search returned
                    json_resp = search_response.json()
                    self.search_results_count = int(json_resp["esearchresult"]["count"])
                    logging.info(f"PubMed API: Search Endpoint: Total Search Results For Current Query: {self.search_results_count}")
                else: 
                    logging.error(f"PubMed API: Search Endpoint: Response NOT OK: {response_code}")
                    return
            except Exception as e:
                logging.error(f"Search Endpoint: Likely Not Related To Endpoint: {e}")
                return

                
            if self.api_key:
                logging.info(f"Search Endpoint: Sleeping For {PM_API_SLEEP_TIME['with_key']}s.")
                time.sleep(PM_API_SLEEP_TIME["with_key"])    #with an api key, we are allowed to do 10req/second
            else: 
                logging.info(f"Search Endpoint: Sleeping For {PM_API_SLEEP_TIME['without_key']}s.")
                time.sleep(PM_API_SLEEP_TIME["without_key"]) #without an api key, we only have 3req/second 
            
            return search_response.json()                    
        

    def fetch(self, search_data, max_results=1000, start = 0, db = "pubmed", pmc_id = None, rettype = 'abstract'):
            """ 
        for PubMed Central API:
                db = 'pmc'
                pmc_id = string pmc id without the PMC prefixe
                rettype = 'full' 
                start = is for retstart API param, PubMed Documentation: 
        Sequential index of the first record to be retrieved
        (default=0, corresponding to the first record of the entire set).
        This parameter can be used in conjunction with retmax to download 
        an arbitrary subset of records from the input set.
                """
            # step2: fetching (either using history if PubMed API, or using mpc_id if PubMedCentral API) 
            fetch_url = f"{self.base_url}efetch.fcgi"
            fetch_post_data = {
                'db': db,
                'retmode': 'xml',   #json is not available for fetch endpoint
                'rettype': rettype, #"abstract" if PubMed else "full"
            }
        
            #adding history params and max results only if dealing with PubMed API 
            if pmc_id is None: #which means that we are using PubMed API, we already have the search_data.
                fetch_post_data['WebEnv'] = search_data['esearchresult']['webenv']
                fetch_post_data['query_key'] = search_data['esearchresult']['querykey']
                fetch_post_data['retmax'] = max_results
                fetch_post_data['retstart'] = start
                if self.api_key: fetch_post_data['api_key'] = self.api_key
                if self.email: fetch_post_data['email'] = self.email
            else: #which means that we are using PMC API, we have an id.
                fetch_post_data['id'] = pmc_id 

                if self.api_key:
                    fetch_post_data['api_key'] = self.api_key

                if self.email:
                    fetch_post_data['email'] = self.email
                

            try: 
                fetch_response = rq.post(fetch_url, data=fetch_post_data, headers=self.headers)
                response_code = fetch_response.status_code
                if pmc_id is None: #pubmed API
                    if response_code == 200: 
                        logging.info(f"PubMed API: Fetch Endpoint: Response OK: {response_code}")
                    else: 
                        logging.warning(f"PubMed API: Fetch Endpoint: Response NOT OK: {response_code}")
                else: #pubmedcentral API
                    if response_code == 200: 
                        logging.info(f"PubMedCentral API: Fetch Endpoint: Response OK: {response_code}")
                    else: 
                        logging.error(f"PubMedCentral API: Fetch Endpoint: Response NOT OK: {response_code}")
            except Exception as e: 
                logging.error(f"Fetch Endpoint: Error: {e}")
                return None
                        
            if self.api_key: 
                logging.info(f"Fetch Endpoint: Sleeping For {PM_API_SLEEP_TIME['with_key']}s.")
                time.sleep(PM_API_SLEEP_TIME["with_key"])  
            else: 
                logging.info(f"Fetch Endpoint: Sleeping For {PM_API_SLEEP_TIME['without_key']}s.")
                time.sleep(PM_API_SLEEP_TIME["without_key"])   
            
            return fetch_response #xml that contains the data of searched articles
                                #(resp. article with pmc_id)
                                # if we are using PM API (resp. PMC API)
        
        

        
    def get_data_from_xml(self, fetch_response): #this is only for the PubMed API, I @override it for MPC API.
        if fetch_response: 
            root = ET.fromstring(fetch_response.text)
            articles = [] 
            found = root.findall('.//PubmedArticle')
            if len(found) > 0: 
                logging.info(f"PubMed API: Found {len(found)} Articles In Fetched XML Root.")
            else: 
                logging.warning(f"PubMed API: Found {len(found)} Articles In Fetched XML Root.")

            for article in found:
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
                logging.info(f"PubMed API: PMid: {article_pmid.text}: Metadata Found.")
            
            return articles #list of dicts, each dict is an article's metadata containing the keys above.
        else: 
            return []
    

    def normalize_term(self, term):
    
        search_url = f"{self.base_url}esearch.fcgi"
        search_params = {
            'db': 'mesh',
            'term': term,
            'retmax': 1,  # Only get the best match
            'retmode': 'json'
        }
        
        if self.api_key:
            search_params['api_key'] = self.api_key
        if self.email:
            search_params['email'] = self.email
        
        try:
            # Search MeSH database
            search_response = rq.get(search_url, params=search_params, headers=self.headers)
            if search_response.status_code != 200:
                return None
                
            search_data = search_response.json()
            
            # Rate limiting
            if self.api_key:
                time.sleep(PM_API_SLEEP_TIME["with_key"])
            else:
                time.sleep(PM_API_SLEEP_TIME["without_key"])
            
            # Check if we found any results
            id_list = search_data.get('esearchresult', {}).get('idlist', [])
            if not id_list:
                return None
            
            # Fetch the MeSH term details
            fetch_url = f"{self.base_url}efetch.fcgi"
            fetch_post_data = {
                'db': 'mesh',
                'id': id_list[0],  # Get the first (best) match
                'retmode': 'xml'
            }
            
            if self.api_key:
                fetch_post_data['api_key'] = self.api_key
            if self.email:
                fetch_post_data['email'] = self.email
            
            fetch_response = rq.get(fetch_url, params=fetch_post_data, headers=self.headers)
            if fetch_response.status_code != 200:
                return None
            
            # Rate limiting
            if self.api_key:
                time.sleep(PM_API_SLEEP_TIME["with_key"])
            else:
                time.sleep(PM_API_SLEEP_TIME["without_key"])
            
            # Parse the MeSH term
            root = ET.fromstring(fetch_response.text)
            mesh_term = root.find('.//DescriptorName/String')
            
            return mesh_term.text if mesh_term is not None else None
            
        except Exception as e:
            logging.error(f"Normalization failed for '{term}': {e}")
            return None


