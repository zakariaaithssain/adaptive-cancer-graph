from scripts.extract import extract_pubmed_to_mongo
from scripts.transform.annotate import annotate_mongo_articles
from scripts.transform.clean import prepare_data_for_neo4j
#less max_results, less API pression, more loop iterations
#if max results is not specified, the default is 1k, the max is 10k
#extract_abstracts_only = False to get also bodies for each article if available in PubMedCentral
extract_pubmed_to_mongo(extract_abstracts_only=True, max_results=1000)  

#this runs NER, RE, and Linking (normalization), and saves extracted entities and relations 
#to two separate csv files.
annotate_mongo_articles()

#this takes the csvs from the last step and clean and make them compatible to Neo4j. 
extracted_entities = "data/extracted_entities.csv"
extracted_relations = "data/extracted_relations.csv"
saving_dir = "data/ready_for_neo4j"
prepare_data_for_neo4j(raw_ents_path=extracted_entities,
                       raw_rels_path=extracted_relations, 
                       saving_dir=saving_dir)

#implement the loading script.
