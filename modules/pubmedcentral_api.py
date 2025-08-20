from xml.etree import ElementTree as ET
from typing import override

import logging
import pickle
import os 

from modules.pubmed_api import PubMedAPI


#PubMed Central API to get the body text of free available articles. 
class PubMedCentralAPI(PubMedAPI): 
    def __init__(self, api_key = None, email = None):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.api_key = api_key
        self.email = email
        self.headers = { "User-Agent": "MyResearchBot/1.0 (zakaria04aithssain@gmail.com)" }

        if api_key: logging.info("PubMedCentral API: API Key Used.")
        else: logging.warning("PubMedCentral API: API Key Absent.")

        if self.email: logging.info("PubMedCentral API: Email Used.\n")
        else: logging.warning("PubMedCentral API: Email Absent.\n")

        #load pmcids cache 
        self.pmcids_cache = set()
        self._load_cache()

    @override             
    def get_data_from_xml(self, pmc_id):
        if pmc_id is not None and pmc_id not in self.pmcids_cache:
            self.pmcids_cache.add(pmc_id)
            search_result = self.search(db="pmc", pmc_id= pmc_id, rettype="full")
            response_xml =self.fetch(search_result, db="pmc", pmc_id= pmc_id, rettype="full")
            if response_xml: 
                root = ET.fromstring(response_xml.text)

                article_body = root.find(".//body")
                if article_body is None:
                    return None

                paragraphs = []
                for p in article_body.findall(".//p"):
                    if p.text: 
                        paragraphs.append(p.text.strip())
                
                
                return "\n\n".join(paragraphs)
            
    

    @override
    def _load_cache(self):
        """Load PMCids cache from disk if it exists."""
        try:
            with open('cache/pmcids_cache.pkl', 'rb') as f:
                self.pmcids_cache = pickle.load(f)
            logging.info(f"PubMed API: Loaded {len(self.pmcids_cache)} cached pmcids")
        except FileNotFoundError:
            logging.info("PubMed API: No existing cache found, starting fresh")
    
    
    @override
    def _save_cache(self):
        """Save PMCids cache to disk."""
        try:
            os.makedirs("cache", exist_ok=True)
            with open('cache/pmcids_cache.pkl', 'wb') as f:
                pickle.dump(self.pmcids_cache, f)
            logging.info(f"PubMed API: Saved {len(self.pmcids_cache)} pmcids to cache")
        except Exception as e:
            logging.error(f"PubMed API: Failed to save cache: {e}")
    
        
        



    

