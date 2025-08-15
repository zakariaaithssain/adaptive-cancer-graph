import pandas as pd

import spacy
import logging

from spacy.matcher import Matcher, DependencyMatcher

from modules.umls_api import UMLSNormalizer
from modules.umls_api import UMLSNormalizer
from config.nlp_config import MATCHER_PATTERNS, DEPENDENCY_MATCHER_PATTERNS

#this uses a clever pandas usage to remove duplications from entities and relations of each article.

class NLP:
   def __init__(self, normalizer : UMLSNormalizer):
      logging.info("NLP: Loading NER Model...")
      print("loading ner model...")
      self.nlp_pipe = spacy.load("en_ner_bionlp13cg_md") 
      self.nlp_pipe.add_pipe("merge_entities", after="ner")
      self.entities= []
      self.relations = []
      #initialize matchers with model vocab
      self.matcher = Matcher(self.nlp_pipe.vocab)
      self.dep_matcher = DependencyMatcher(self.nlp_pipe.vocab)
      #initialize the normalizer (it's simply an API )
      #I guess scispacy has a Linker class to UMLS but it's sooooooooo heavy.
      self.normalizer = normalizer

      #add patterns to matchers
      for label, patterns in MATCHER_PATTERNS.items():
         self.matcher.add(label, patterns)

      for label, patterns in DEPENDENCY_MATCHER_PATTERNS.items():
         self.dep_matcher.add(label, patterns) 

   
   #NER using en_ner_bionlp13cg_md scispacy model.
   def extract_and_normalize_entities(self, text, article_metadata : dict):
      doc = self.nlp_pipe(text)
      entities = []
      for ent in doc.ents:
         if __name__ == "__main__": print(f"entity: {ent.text} --- label: {ent.label_}\n ******* ")

         #updating the entities with metadata of the article they were extracted from
         text = ent.text
         entity_dict = {
                        "text": text.strip().lower(), #to avoid duplications due to capitalization
                        "label": ent.label_,
                        #dict unpacking or whatever they call this **
                        #unpacking the attrs returned from UMLS API about the text.
                        ** self.normalizer.normalize(text), 
                        #unpacking metadate of the article to know where the entity was found
                        **article_metadata 
                           }
         
         entities.append(entity_dict) 

      
      unique_entities = pd.DataFrame(entities).drop_duplicates().to_dict('records')
      self.entities.extend(unique_entities)
      
      return self

#rule based and dependency based ER, so it's not that accurate like Model based ER.
   def extract_relations(self, text, article_metadata):
    doc = self.nlp_pipe(text)
    
    matches = self.matcher(doc)
    dep_matches = self.dep_matcher(doc)
    
    relations = []
    
    # Matcher-based relations
    for match_id, start, end in matches:
        entities_in_span = [ent for ent in doc.ents if ent.start >= start and ent.end <= end]
        
        if len(entities_in_span) == 2:
            ent1, ent2 = entities_in_span
            relation_label = self.nlp_pipe.vocab.strings[match_id]
            
            if __name__ == "__main__":
                print(f"{ent1.text} -[{relation_label}]-> {ent2.text}\n*******")
            
            #unpacking the dict of normalizer inside this will cause not knowing to which entity
            #the normalization data belong, so I guess I'll join relations and entities tables
            # on pmid in order to normalize ent1 and ent2 for each relation
            rel_dict = {
                "ent1": ent1.text.strip().lower(),
                "relation": relation_label,
                "ent2": ent2.text.strip().lower(),
                **article_metadata
            }
            relations.append(rel_dict)
    
    # Dependency-matcher-based relations
    for match_id, token_ids in dep_matches:
        relation_label = self.nlp_pipe.vocab.strings[match_id]
        ent1 = doc[token_ids[0]]
        ent2 = doc[token_ids[-1]]
        
        if __name__ == "__main__":
            print(f"{ent1.text} -[{relation_label}]-> {ent2.text}\n*******")
        
        rel_dict = {
            "ent1": ent1.text,
            "relation": relation_label,
            "ent2": ent2.text,
            **article_metadata
        }
        relations.append(rel_dict)
    
    unique_relations = pd.DataFrame(relations).drop_duplicates().to_dict('records')
    
    self.relations.extend(unique_relations)
    return self

   def generate_entities_csv(self, file_path = "data/extracted_entities.csv"):
      if self.entities == []:
         logging.warning("NLP: No Entities In self.entities. Make Sure To Extract Them First.")
         print("no entities found extract first.")
         df = pd.DataFrame(data = [{"entity": "", "label": ""}])
      else: 
         df = pd.DataFrame(data = self.entities)
      
      try:
         df.to_csv(file_path, index=False)
         logging.info(f"NLP: Entities Saved To {file_path}")
         print("entities saved to data/entities.csv")
      except Exception as e:
         logging.error(f"NLP: Failed To Save Entities As SCV: Error: {e}")
         print("error while saving entities to scv.")
      return self
   


   def generate_relations_csv(self, file_path = "data/extracted_relations.csv"):
      if self.relations == []:
         logging.warning("NLP: No Relations In self.relations. Make Sure To Extract Them First.")
         print("no relations found extract first.")

         df = pd.DataFrame(data = [{"ent1": "", "relation": "", "ent2": ""}])
      else: 
         df = pd.DataFrame(data = self.relations)
      
      try:
         df.to_csv(file_path, index=False)
         logging.info(f"NLP: Relations Saved To {file_path}")
         print("entities saved to data/relations.csv")
      except Exception as e:
         logging.error(f"NLP: Failed To Save Relations As SCV: Error: {e}")
         print("error while saving relations to csv.")
      return self

#printing entities recognized by the model if running as main.
if __name__ == "__main__": 
   normalizer = UMLSNormalizer()
   nlp = NLP(normalizer=normalizer) 
   print("Entities recognized by ner_bionlp13cg_md model:")
   print(nlp.nlp_pipe.get_pipe("ner").labels)
   if not nlp.entities: print("no entities, make sure to extract them.")
   elif not nlp.relations: print("no relations, make sure to extract them.")
   else: print(nlp.entities, nlp.relations, sep= "\n *** \n")

