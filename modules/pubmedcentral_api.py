from xml.etree import ElementTree as ET
from typing import override

import logging

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

    @override             
    def get_data_from_xml(self, pmc_id):
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

        else: 
            return None
        



    

