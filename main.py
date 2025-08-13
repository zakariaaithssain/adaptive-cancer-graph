from scripts.extract import extract_pubmed_to_mongo


#less max_results, less API pression, more loop iterations
#if max results is not specified, the default is 1k, the max is 10k
#extract_abstracts_only = False to get also bodies for each article if available in PubMedCentral
extract_pubmed_to_mongo(extract_abstracts_only=True, max_results=1000)  
