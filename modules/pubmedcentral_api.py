from xml.etree import ElementTree
import requests as rq

import time

from config.apiconfig import API_SLEEP_TIME


#PubMed Central API to get the body text of free available articles. 
#re create this class to get the body text of the articles using the pmcid provided in the scripts.api
class PubMedCentralAPI:
    def __init__(self, api_key = None, email = None):
        self.linking_endpoint = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
        self.api_key = api_key
        self.email = email
