import spacy

from spacy.matcher import Matcher, DependencyMatcher

from config.nlp_config import MATCHER_PATTERNS, DEPENDENCY_MATCHER_PATTERNS


class NLP:
   def __init__(self):
      self.nlp_pipe = spacy.load("en_ner_bionlp13cg_md") 
      self.nlp_pipe.add_pipe("merge_entities", after="ner")



   # Initialize matchers
      self.matcher = Matcher(self.nlp_pipe.vocab)
      self.dep_matcher = DependencyMatcher(self.nlp_pipe.vocab)

   # Add patterns to matchers
      for label, patterns in MATCHER_PATTERNS.items():
         self.matcher.add(label, patterns)

      for label, patterns in DEPENDENCY_MATCHER_PATTERNS.items():
         self.dep_matcher.add(label, patterns) 

   

   def extract_entities_and_relations(self, text):
      doc = self.nlp_pipe(text)
      entities = []
      for ent in doc.ents:
         if __name__ == "__main__": print(f"entity: {ent.text} --- label: {ent.label_}\n ******* ")
         entities.append((ent.text, ent.label_))

      relations = []

      # Matcher results
      matches = self.matcher(doc)
      for match_id, start, end in matches:
         # Get entities fully inside the matched span
         entities_in_span = [ent for ent in doc.ents if ent.start >= start and ent.end <= end]
         if len(entities_in_span) == 2:
               ent1, ent2 = entities_in_span
               relation = self.nlp_pipe.vocab.strings[match_id]
               if __name__ == "__main__": print(f"{ent1.text} -[{relation}]-> {ent2.text}\n ******* ")
               relations.append((ent1.text, relation, ent2.text))

      # Dependency matcher results
      dep_matches = self.dep_matcher(doc)
      for match_id, token_ids in dep_matches:
         relation = self.nlp_pipe.vocab.strings[match_id]
         ent1 = doc[token_ids[0]]
         ent2 = doc[token_ids[-1]]
         if __name__ == "__main__": print(f"{ent1.text} -[{relation}]-> {ent2.text}\n ******* ")
         relations.append((ent1.text, relation, ent2.text))

      return {"entities": entities, "relations": relations}

if __name__ == "__main__": 
   nlp = NLP() 
   print(nlp.nlp_pipe.get_pipe("ner").labels)

