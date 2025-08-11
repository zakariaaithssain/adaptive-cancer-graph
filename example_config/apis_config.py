API_KEY_EMAIL = {"api_key" : "GET YOUR API KEY JUST BY SIGNING IN TO THE PUBMED WEBSITE IT IS THIS EASY.", 
              
              "email" : "REPLACE WITH THE EMAIL YOU USED FOR SIGNING IN",  
              }



API_SLEEP_TIME = {"with_key" : 0.11,  #with key we have 10requests/second
                  
                  "without_key" : 0.34 #without key we have 3requests/second
                  } 



#the medline[sb] filter is to get data from the Medline Subset of PubMed that contains more high quality data
QUERIES = {       
    "stomach": '''("Stomach Neoplasms"[MeSH] OR "gastric cancer" OR "stomach cancer") AND  
                  ("Genes, Tumor Suppressor"[MeSH] OR "Oncogenes"[MeSH] OR "gene expression" OR "genetic markers" OR 
                   "Mutation"[MeSH] OR "point mutation" OR "chromosomal aberration" OR "genetic variation" OR 
                   "Risk Factors"[MeSH] OR "environmental exposure" OR "lifestyle factors" OR "family history" OR 
                   "Drug Therapy"[MeSH] OR "chemotherapy" OR "targeted therapy" OR "immunotherapy" OR "surgical treatment" OR 
                   "Neoplastic Stem Cells"[MeSH] OR "epithelial cells" OR "stromal cells" OR "immune cells" OR "cell line" OR 
                   "Proteins"[MeSH] OR "tumor markers" OR "biomarkers" OR "protein expression" OR 
                   "adenocarcinoma" OR "signet ring cell" OR "diffuse type" OR "intestinal type") 
                  AND medline[sb] AND "free full text"[sb]''', 

    "prostate": '''("Prostatic Neoplasms"[MeSH] OR "prostate cancer" OR "prostate carcinoma") AND     
                   ("Genes, Tumor Suppressor"[MeSH] OR "Oncogenes"[MeSH] OR "BRCA1" OR "BRCA2" OR "TP53" OR "PTEN" OR 
                    "Mutation"[MeSH] OR "somatic mutation" OR "germline mutation" OR "chromosomal instability" OR 
                    "Risk Factors"[MeSH] OR "age factors" OR "race factors" OR "dietary factors" OR "hormonal factors" OR 
                    "Drug Therapy"[MeSH] OR "androgen deprivation therapy" OR "radiation therapy" OR "prostatectomy" OR "active surveillance" OR 
                    "Epithelial Cells"[MeSH] OR "prostate epithelial cells" OR "cancer stem cells" OR "tumor microenvironment" OR 
                    "Prostate-Specific Antigen"[MeSH] OR "PSA" OR "androgen receptor" OR "tumor suppressor proteins" OR 
                    "adenocarcinoma" OR "Gleason score" OR "neuroendocrine" OR "ductal carcinoma") 
                   AND medline[sb] AND "free full text"[sb]'''
}