import pandas as pd

import spacy
import logging

from spacy.matcher import Matcher, DependencyMatcher

from config.nlp_config import MATCHER_PATTERNS, DEPENDENCY_MATCHER_PATTERNS


class NLP:
   def __init__(self):
      self.nlp_pipe = spacy.load("en_ner_bionlp13cg_md") 
      logging.info("NLP: NER Model Loaded.")
      self.nlp_pipe.add_pipe("merge_entities", after="ner")
      self.entities= []
      self.relations = []
      #initialize matchers with model vocab
      self.matcher = Matcher(self.nlp_pipe.vocab)
      self.dep_matcher = DependencyMatcher(self.nlp_pipe.vocab)

      #add patterns to matchers
      for label, patterns in MATCHER_PATTERNS.items():
         self.matcher.add(label, patterns)

      for label, patterns in DEPENDENCY_MATCHER_PATTERNS.items():
         self.dep_matcher.add(label, patterns) 

   
   #NER using en_ner_bionlp13cg_md scispacy model.
   def extract_entities(self, text, article_metadata):
      doc = self.nlp_pipe(text)
      entities = set() #to get rid of duplicated entities in the text
      for ent in doc.ents:
         if __name__ == "__main__": print(f"entity: {ent.text} --- label: {ent.label_}\n ******* ")

         #updating the entities with metadata of the article they were extracted from
         entity = {"text": ent.text, "label": ent.label_}
         entity.update(article_metadata)
         entities.add(frozenset(entity.items())) 
      if len(list(entities)): print(list(entities))
      entities_list = [dict(fs) for fs in entities]
      self.entities.extend(entities_list)
      return self

#rule based and dependency based ER, so it's not that accurate like Model based ER.
   def extract_relations(self, text, article_metadata):
    doc = self.nlp_pipe(text)
    
    matches = self.matcher(doc)
    dep_matches = self.dep_matcher(doc)
    
    relations = set()  # Deduplicate relations
    
    # Matcher-based relations
    for match_id, start, end in matches:
        entities_in_span = [ent for ent in doc.ents if ent.start >= start and ent.end <= end]
        
        if len(entities_in_span) == 2:
            ent1, ent2 = entities_in_span
            relation_label = self.nlp_pipe.vocab.strings[match_id]
            
            if __name__ == "__main__":
                print(f"{ent1.text} -[{relation_label}]-> {ent2.text}\n*******")
            
            rel_dict = {
                "ent1": ent1.text,
                "relation": relation_label,
                "ent2": ent2.text,
                **article_metadata
            }
            relations.add(frozenset(rel_dict.items()))
    
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
        relations.add(frozenset(rel_dict.items()))
    
    # Convert set of frozensets back to list of dicts
    relations_list = [dict(fs) for fs in relations]

    
    if relations_list:
        print(relations_list)
        exit(0)
    
    self.relations.extend(relations_list)
    return self

   def generate_entities_csv(self, file_path = "data/extracted_entities.csv"):
      if self.entities == []:
         logging.warning("NLP: No Entities In self.entities. Make Sure To Extract Them First.")
         df = pd.DataFrame(data = [{"entity": "", "label": ""}])
      else: 
         df = pd.DataFrame(data = self.entities)
      
      try:
         df.to_csv(file_path)
         logging.info(f"NLP: Entities Saved To {file_path}")
      except Exception as e:
         logging.error(f"NLP: Failed To Save Entities As SCV: Error: {e}")
      return self
   


   def generate_relations_csv(self, file_path = "data/extracted_relations.csv"):
      if self.relations == []:
         logging.warning("NLP: No Relations In self.relations. Make Sure To Extract Them First.")
         df = pd.DataFrame(data = [{"ent1": "", "relation": "", "ent2": ""}])
      else: 
         df = pd.DataFrame(data = self.entities)
      
      try:
         df.to_csv(file_path)
         logging.info(f"NLP: Relations Saved To {file_path}")
      except Exception as e:
         logging.error(f"NLP: Failed To Save Relations As SCV: Error: {e}")
      return self

#printing entities recognized by the model if running as main.
if __name__ == "__main__": 
   nlp = NLP() 
   print("Entities recognized by ner_bionlp13cg_md model:")
   print(nlp.nlp_pipe.get_pipe("ner").labels)
   if not nlp.entities: print("no entities, make sure to extract them.")
   elif not nlp.relations: print("no relations, make sure to extract them.")
   else: print(nlp.entities, nlp.relations, sep= "\n *** \n")

