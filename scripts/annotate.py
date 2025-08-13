import logging

from tqdm import tqdm

from modules.mongo_connector import MongoAtlasConnector
from modules.nlp import NLP


def annotate_mongo_articles():
    connector = MongoAtlasConnector()
    annotator = NLP() #one for all so entities and relations could be saved in the class attr.
    try: 
        articles = connector.fetch_articles_from_cloud() #list[dict] each dict is an article
        logging.info("Starting Annotation Process.")
        for article in tqdm(articles):
            text = article.pop('text')
            #we are able to chain methods as we return self from each one
            (annotator.extract_entities(text, article_metadata= article)
                      .extract_relations(text, article_metadata= article))    
        
        annotator.generate_entities_csv().generate_relations_csv()
    except KeyboardInterrupt: 
        logging.error("Annotation Process Interrupted Manually.")


if __name__ == "__main__": 
    annotate_mongo_articles()