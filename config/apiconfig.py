API_KEY_EMAIL = {"api_key" : "2bc8ee871fd9fe3c9b41e25706d430b5fa09", 
              
              "email" : "zakaria04aithssain@gmail.com", 
              }



API_SLEEP_TIME = {"with_key" : 0.11,  #with key we have 10requests/second
                  
                  "without_key" : 0.34 #without key we have 3requests/second
                  } 

QUERIES = {       
                   "stomach" :  '''("Stomach Neoplasms"[MeSH] OR "stomach cancer") AND  
                                ("Genes"[MeSH] OR gene OR 
                                    "Mutation"[MeSH] OR mutation OR 
                                    "Risk Factors"[MeSH] OR "risk factor" OR 
                                    "Drug Therapy"[Subheading] OR treatment OR 
                                    "Tumor Cells"[MeSH] OR tumor OR 
                                    "Cells"[MeSH] OR cell)''', 


                    "prostate" : '''("Prostatic Neoplasms"[MeSH] OR "prostate cancer") AND     
                                    ("Genes"[MeSH] OR gene OR 
                                    "Mutation"[MeSH] OR mutation OR 
                                    "Risk Factors"[MeSH] OR "risk factor" OR 
                                    "Drug Therapy"[Subheading] OR treatment OR 
                                    "Tumor Cells"[MeSH] OR tumor OR 
                                    "Cells"[MeSH] OR cell)'''
}



