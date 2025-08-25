import requests as rq
import xml.etree.ElementTree as ET

import time
import logging
import pickle

from pathlib import Path

from config.apis_config import PM_API_SLEEP_TIME

#TODO: CHANGE EVERYTHING: 
# keep the old class while creating the new one
#  make sure you are on new-extraction-logic branch.
#  the logic will now be: 
"""1 - get all pmids per query from esearch endpoint
   2 - store them in cache
   3 - fetch articles that correspond to mpids that are not in cache
I guess that using this new logic, using the date API param will be useless."""






class NewPubMedAPI:

    """I got this from PubMed API Documentation:
To retrieve more than 10,000 UIDs from databases other than PubMed,
submit multiple esearch requests while incrementing the value of retstart (Me: I implemented this).
For PubMed, ESearch can only retrieve the first 10,000 records matching the query.
(Me: If using pubmed database and the wanted number of results is more than 10,000, will only return 10,000)
To obtain more than 10,000 PubMed records, consider using <EDirect> (Me: it's a CLI lol) that contains additional logic
to batch PubMed search results automatically so that an arbitrary number can be retrieved."""

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

        #the hard coded limit of how much results can PubMed API return per call (10^4)
        self.hard_limit = int(1e4)
        #cache: 
        self.pmids_cache = set()
        self.cache_path = Path("cache/pmids_cache.pkl")
        #load old pmids cache
        self._load_cache()


    def get_pmids(self, query:str, database = 'pubmed', max_results:int = None):
        """Add all pmids that are returned by a query to self.cache
            Params: 
                    query: a query like the one we would write in the search bar
                    database: a database supported by PubMedAPI (default = 'pubmed')
                            see this for all available databases: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi

                            NOTE: only for pubmed database, ESearch can only retrieve the first 10,000 records matching the query
                                (so 'retstart' cannot be larger than 9998)
                                To obtain more than 10,000 PubMed records, consider using <EDirect> (it's a CLI) so that an arbitrary number can be retrieved.
                    max_results: the number of pmids to get per query, if not specified, we get everything available
                                if database = 'pubmed', the max we can get is 10,000 records. """
        
        post_data = {
            'db': database,        #database to use (pubmed is default)
            'term': query,  
            'retmode': 'json',     #json is available as a return type for esearch endpoint
        }
            
        #set API key and email if used
        if self.api_key:
            post_data['api_key'] = self.api_key
        if self.email:
            post_data['email'] = self.email

        #how many results to get
        if isinstance(max_results, int) and max_results <= self.hard_limit:
            # add 'retmax' to HTTP POST data
            post_data['retmax'] = max_results

            response = self._send_post_request(post_data)
            if response:
                ids : list = response.json()['esearchresult']['idlist']
                self.pmids_cache.update(set(ids))
        
        else: #either None or greater than hard_limit
            if database == 'pubmed':
                # Esearch can only get 10000 records from pubmed database
                logging.warning("PubMed API: For 'pubmed' database, ESearch Endpoint is built to only retrieve the first 10,000 records matching the query. " \
                "To get more, either specify another database or use EDirect (a CLI).")
                print("max results for 'pubmed' database is 10,000. See logs file for more info.")
                post_data['retmax'] = self.hard_limit
                response = self._send_post_request(post_data)
                if response:
                    ids : list = response.json()['esearchresult']['idlist']
                    self.pmids_cache.update(set(ids))
            else: #we don't have the 10,000 constraint with other databases

                post_data['retmax'] = self.hard_limit
            
                #if max_results is not specified, we will get everything available by setting it to count.
                if max_results is None:
                    temp_response = self._send_post_request(post_data)
                    count = int(temp_response.json()['esearchresult']['count'])
                    logging.info(f"PubMed API: max_results is not specified, getting all {count} results found.")
                    max_results = count

                # + 1 for an additional iteration to get the remaining if max_results % hard_limit != 0
                for _ in range((max_results // self.hard_limit) + 1): 
                    response = self._send_post_request(post_data)
                    if response:
                        ids : list = response.json()['esearchresult']['idlist']
                        self.pmids_cache.update(set(ids))

                        # default: 'retstart' = 0 corresponds to the first result in the search list
                        post_data['retstart'] = self.hard_limit
        
        self._save_cache()
        


        
    def _send_post_request(self, data_to_post: dict):
        """Send a HTTP POST request to PubMed API esearch endpoint.
           Params: 
           data_to_post: data to post (passed to requests.post() data argument)"""
        search_url = f"{self.base_url}esearch.fcgi"
        try: #get recieves params, post recieves data
            post_response = rq.post(search_url, data_to_post, headers=self.headers)
            response_code = post_response.status_code
            if response_code == 200:
                logging.info(f"PubMed API: Search Endpoint: Response OK: {response_code}")
                
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
        
        return post_response                   




    def _load_cache(self):
        try:
            with open(self.cache_path, "rb") as f: 
                self.pmids_cache = pickle.load(f)
                logging.info(f"PubMed API: loaded {len(self.pmids_cache)} cached pmids.")
        except FileNotFoundError:
            logging.info(f"PubMed API: no cache found, starting fresh.")



    
    def _save_cache(self):
        #make sure the path exists 
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.cache_path, "wb") as f: 
                pickle.dump(obj= self.pmids_cache, file= f)
                logging.info(f"PubMed API: saved {len(self.pmids_cache)} pmids to cache.")
        except Exception as e: 
            logging.error(f"PubMed API: failed to save pmids to cache. {e}")




if __name__ == "__main__":
    api = NewPubMedAPI()
    
    api.get_pmids(query="human")
    print(len(api.pmids_cache))

































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
    

    
    def search(self, query = None, max_results=1000, db = "pubmed", pmc_id = None, retstart = 0): 
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
                'retstart': retstart,
                'retmode': 'json',    #json is available as a return type for search endpoint
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
                    if article_pmcid is not None: break
                
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
        else: 
            return []
    



