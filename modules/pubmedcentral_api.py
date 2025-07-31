from xml.etree import ElementTree as ET
from typing import override

import logging

from modules.pubmed_api import PubMedAPI


#PubMed Central API to get the body text of free available articles. 
class PubMedCentralAPI(PubMedAPI): 
    def __init__(self, api_key = None, email = None):
        #the two APIs have the same base url, endpoints, email, key, and some params
        super().__init__() 
                        
    @override
    def get_data_from_xml(self, pmc_id):
        logging.info(f"PubMedCentral API: Article PMCid: {pmc_id}: Looking For Article Content.")
        response_xml = self.search_and_fetch(db="pmc", pmc_id= pmc_id, rettype="full")
        root = ET.fromstring(response_xml.text)

        article_body = root.find(".//body")
        if article_body is None:
            logging.warning(f"PubMedCentral API: Article PMCid: {pmc_id}: Content Not Found.")
            return None

        paragraphs = []
        for p in article_body.findall(".//p"):
            if p.text: 
                paragraphs.append(p.text.strip())
        
        if paragraphs: 
            logging.info(f"PubMedCentral API: Article PMCid: {pmc_id}: Content Found.")
        return "\n\n".join(paragraphs)

        



    

