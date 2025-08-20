import logging

from tqdm import tqdm

from modules.mongoatlas import MongoAtlasConnector
from modules.umls_api import UMLSNormalizer
from modules.nlp import StreamingOptimizedNLP

from config.mongodb_config import CONNECTION_STR




def annotate_mongo_articles(raw_ents_path ="data/extracted_entities.csv", raw_rels_path = "data/extracted_relations.csv"):
    
    connector = MongoAtlasConnector(connection_str=CONNECTION_STR)
    #list[dict] each dict is an article
    articles = connector.fetch_articles_from_atlas(query={})
        
    #one for all so entities and relations could be saved in the class attr.
    normalizer = UMLSNormalizer()
    annotator = StreamingOptimizedNLP(
        normalizer=normalizer,
        entities_output_path=raw_ents_path,
        relations_output_path=raw_rels_path,
    )


    logging.info("Annotation Process Started.")
    try:
        for article in tqdm(articles, desc="Applying NLP over Mongo docs:"):
            text = article.pop('text')
            #we are able to chain methods as we return self from each one
            (annotator.extract_and_normalize_entities(text, article_metadata= article)
                    .extract_relations(text, article_metadata= article))    
        
    except KeyboardInterrupt: 
        logging.error("Annotation Process Interrupted Manually.")
        raise
    