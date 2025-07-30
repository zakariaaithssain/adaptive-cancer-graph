from xml.etree import ElementTree
import requests as rq

import time

from config.apiconfig import API_SLEEP_TIME



class PMCAPI:
    def __init__(self, api_key = None, email = None):
        self.linking_endpoint = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
        self.api_key = api_key
        self.email = email

    def pmid_to_pmc(self, pmid):
        params = {
            "dbfrom": "pubmed",
            "linkname": "pubmed_pmc",  # links pubmed to pmc
            "id": pmid,
            "retmode": "xml"
        }

        if self.api_key: params["api_key"] = self.api_key
        if self.email: params["email"] = self.email

        response = rq.get(self.linking_endpoint, params=params)

        if self.api_key: API_SLEEP_TIME["with_key"]   #with an api key, we are allowed to do 10req/second
        else: API_SLEEP_TIME["without_key"]           #without an api key, we only have 3req/second 

        root = ElementTree.fromstring(response.content)

        links = root.findall(".//LinkSetDb/Link/Id")
        if links:
            return links[0].text  # return the first pmc id explicitly
        
        return None #no pmc id available


    def get_fulltext_from_pmc(self, pmc_id):

        url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC{pmc_id}/unicode"
        response = rq.get(url)

        if self.api_key: time.sleep(API_SLEEP_TIME["with_key"])   # e.g., 0.1
        else: time.sleep(API_SLEEP_TIME["without_key"])  # e.g., 0.34

        # check status and content type
        if response.status_code == 200 and response.headers.get("Content-Type") == "application/json":
            return response.json()
        else:
            print(f"[WARN] PMC{pmc_id} returned status {response.status_code} with content-type {response.headers.get('Content-Type')}")
            print("Response preview:", response.text[:200])  # first 200 characters
            return None

        
    def parse_fulltext(self, pmc_id):

        if pmc_id:
            full_text = self.get_fulltext_from_pmc(pmc_id)
            try: 
                for passage in full_text["documents"][0]["passages"]:
                    if passage["infons"].get("section_type") == "body": print(passage["text"])
            
            except TypeError: 
                pass 
        else: print("pmc_id is None")