import requests as rq

import logging

from config.apis_config import UMLS_API_KEY




class UMLSNormalizer:
    def __init__(self):
        self.key = UMLS_API_KEY
        self.base_url = "https://uts-ws.nlm.nih.gov/rest"
    
    def normalize(self, string: str):

        search_url = f"{self.base_url}/search/current"
        params = {
            "apiKey" : self.key,
        #I don't lower because that might affect the search, especially for drugs and mutations
            "string" : string.strip() 
                  }
        
        
        response = rq.get(search_url, params= params)
        status_code = response.status_code
        if status_code == 200: 
            json_output = response.json()
            results = json_output['result']['results']
            #return None if results = [] or no CUI for the term (CUI is a universal id)
            if not results or results[0][ "ui"] == "NONE": 
                return None
            else:
                best_match : dict = results[0]
                #renaming the keys
                best_match['cui'] = best_match.pop('ui')
                best_match['normalized_name'] = best_match.pop('name')
                best_match['normalization_source'] = best_match.pop('rootSource')
                best_match['url'] = best_match.pop('uri')
                return best_match
        else: 
            print("error", status_code)



            
        


if __name__ == "__main__":
    normalizer = UMLSNormalizer()
    #example wssf
    print(normalizer.normalize("human "))