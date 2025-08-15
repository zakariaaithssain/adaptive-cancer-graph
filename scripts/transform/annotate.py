import logging

from tqdm import tqdm

from modules.mongoatlas import MongoAtlasConnector
from modules.umls_api import UMLSNormalizer
from modules.nlp import NLP


def annotate_mongo_articles():
    connector = MongoAtlasConnector()
     
    #list[dict] each dict is an article
    articles = connector.fetch_articles_from_atlas(query={})
    
    #one for all so entities and relations could be saved in the class attr.
    normalizer = UMLSNormalizer()
    annotator = NLP(normalizer) 

    logging.info("Annotation Process Started.")
    try:
        for article in tqdm(articles):
            text = article.pop('text')
            #we are able to chain methods as we return self from each one
            (annotator.extract_and_normalize_entities(text, article_metadata= article)
                    .extract_relations(text, article_metadata= article))    
        
    except KeyboardInterrupt: 
        logging.error("Annotation Process Interrupted Manually.")

    finally: 
        annotator.generate_entities_csv().generate_relations_csv()


if __name__ == "__main__": 
    annotate_mongo_articles()