import pandas as pd
import spacy
import logging
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import pickle
import hashlib
from typing import List, Dict, Set, Optional
import time
from collections import defaultdict

from spacy.matcher import Matcher, DependencyMatcher

from modules.umls_api import UMLSNormalizer
from config.nlp_config import MATCHER_PATTERNS, DEPENDENCY_MATCHER_PATTERNS

class OptimizedNLP:
    def __init__(self, normalizer: UMLSNormalizer, cache_size: int = 10000, batch_size: int = 50, max_workers: int = 4):
        logging.info("NLP: Loading NER Model...")
        print("loading ner model...")
        self.nlp_pipe = spacy.load("en_ner_bionlp13cg_md") 
        self.nlp_pipe.add_pipe("merge_entities", after="ner")
        
        # Initialize storage
        self.entities = []
        self.relations = []
        
        # Initialize matchers with model vocab
        self.matcher = Matcher(self.nlp_pipe.vocab)
        self.dep_matcher = DependencyMatcher(self.nlp_pipe.vocab)
        
        # Initialize the normalizer
        self.normalizer = normalizer
        
        # Performance optimization settings
        self.cache_size = cache_size
        self.batch_size = batch_size
        self.max_workers = max_workers
        
        # Caching and deduplication
        self._normalization_cache = {}
        self._entity_cache = set()  # For fast duplicate checking
        self._relation_cache = set()  # For fast duplicate checking
        self._load_cache()
        
        # Add patterns to matchers
        for label, patterns in MATCHER_PATTERNS.items():
            self.matcher.add(label, patterns)

        for label, patterns in DEPENDENCY_MATCHER_PATTERNS.items():
            self.dep_matcher.add(label, patterns)
    
    def _generate_cache_key(self, text: str) -> str:
        """Generate a hash key for caching normalized entities."""
        return hashlib.md5(text.lower().strip().encode()).hexdigest()
    
    def _load_cache(self):
        """Load normalization cache from disk if it exists."""
        try:
            with open('normalization_cache.pkl', 'rb') as f:
                self._normalization_cache = pickle.load(f)
            logging.info(f"NLP: Loaded {len(self._normalization_cache)} cached normalizations")
        except FileNotFoundError:
            logging.info("NLP: No existing cache found, starting fresh")
    
    def _save_cache(self):
        """Save normalization cache to disk."""
        try:
            with open('normalization_cache.pkl', 'wb') as f:
                pickle.dump(self._normalization_cache, f)
            logging.info(f"NLP: Saved {len(self._normalization_cache)} normalizations to cache")
        except Exception as e:
            logging.error(f"NLP: Failed to save cache: {e}")
    
    def _should_normalize(self, text: str) -> bool:
        """Determine if entity should be normalized (skip very short/common ones)."""
        text = text.strip().lower()
        # Skip very short entities or common stop-words
        skip_patterns = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return len(text) > 2 and text not in skip_patterns
    
    def _batch_normalize_entities(self, entity_texts: List[str]) -> Dict[str, Dict]:
        """Normalize entities in batches to reduce API calls."""
        results = {}
        to_normalize = []
        
        # Check cache first
        for text in entity_texts:
            cache_key = self._generate_cache_key(text)
            if cache_key in self._normalization_cache:
                results[text] = self._normalization_cache[cache_key]
            elif self._should_normalize(text):
                to_normalize.append(text)
            else:
                # Return empty normalization for skipped entities
                results[text] = {"cui": "", "normalized_name": "", "normalization_source": "", "url": ""}
        
        if not to_normalize:
            return results
        
        logging.info(f"NLP: Normalizing {len(to_normalize)} new entities via UMLS API")
        
        # Process in smaller batches to avoid overwhelming the API
        for i in range(0, len(to_normalize), self.batch_size):
            batch = to_normalize[i:i + self.batch_size]
            
            # Use ThreadPoolExecutor for concurrent API calls
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_text = {
                    executor.submit(self.normalizer.normalize, text): text 
                    for text in batch
                }
                
                for future in as_completed(future_to_text):
                    text = future_to_text[future]
                    try:
                        normalization_result = future.result()
                        cache_key = self._generate_cache_key(text)
                        
                        # Cache the result
                        self._normalization_cache[cache_key] = normalization_result
                        results[text] = normalization_result
                        
                    except Exception as e:
                        logging.error(f"NLP: Failed to normalize '{text}': {e}")
                        # Provide empty normalization on failure
                        results[text] = {"cui": "", "normalized_name": "", "normalization_source": "", "url": ""}
            
            # Small delay between batches to be respectful to the API
            if i + self.batch_size < len(to_normalize):
                time.sleep(0.5)
        
        # Save cache periodically
        if len(self._normalization_cache) % 100 == 0:
            self._save_cache()
        
        return results
    
    def extract_and_normalize_entities(self, text: str, article_metadata: dict):
        """Extract entities with optimized normalization."""
        doc = self.nlp_pipe(text)
        
        if not doc.ents:
            return self
        
        # Collect unique entity texts first (deduplication before expensive normalization)
        entity_texts_to_normalize = set()
        extracted_entities = []
        
        for ent in doc.ents:
            if __name__ == "__main__": 
                print(f"entity: {ent.text} --- label: {ent.label_}\n ******* ")
            
            text_normalized = ent.text.strip().lower()
            
            # Create entity dict without normalization first
            entity_dict = {
                "text": text_normalized,
                "label": ent.label_,
                **article_metadata
            }
            
            extracted_entities.append(entity_dict)
            entity_texts_to_normalize.add(ent.text.strip())
        
        # Batch normalize all unique entity texts
        normalization_results = self._batch_normalize_entities(list(entity_texts_to_normalize))
        
        # Apply normalization results to entities
        final_entities = []
        for entity_dict in extracted_entities:
            original_text = None
            # Find the original text (case-sensitive) for this entity
            for ent in doc.ents:
                if ent.text.strip().lower() == entity_dict["text"]:
                    original_text = ent.text.strip()
                    break
            
            if original_text and original_text in normalization_results:
                entity_dict.update(normalization_results[original_text])
            
            # Create a hashable key for deduplication
            entity_key = (
                entity_dict["text"], 
                entity_dict["label"], 
                entity_dict.get("pmid", ""), 
                entity_dict.get("pmcid", "")
            )
            
            # Only add if not already seen
            if entity_key not in self._entity_cache:
                self._entity_cache.add(entity_key)
                final_entities.append(entity_dict)
        
        self.entities.extend(final_entities)
        logging.info(f"NLP: Added {len(final_entities)} new unique entities")
        
        return self
    
    def extract_relations(self, text: str, article_metadata: dict):
        """Extract relations with optimized deduplication."""
        doc = self.nlp_pipe(text)
        
        matches = self.matcher(doc)
        dep_matches = self.dep_matcher(doc)
        
        new_relations = []
        
        # Matcher-based relations
        for match_id, start, end in matches:
            entities_in_span = [ent for ent in doc.ents if ent.start >= start and ent.end <= end]
            
            if len(entities_in_span) == 2:
                ent1, ent2 = entities_in_span
                relation_label = self.nlp_pipe.vocab.strings[match_id]
                
                if __name__ == "__main__":
                    print(f"{ent1.text} -[{relation_label}]-> {ent2.text}\n*******")
                
                rel_dict = {
                    "ent1": ent1.text.strip().lower(),
                    "relation": relation_label,
                    "ent2": ent2.text.strip().lower(),
                    **article_metadata
                }
                
                # Create hashable key for deduplication
                relation_key = (
                    rel_dict["ent1"],
                    rel_dict["relation"],
                    rel_dict["ent2"],
                    rel_dict.get("pmid", ""),
                    rel_dict.get("pmcid", "")
                )
                
                if relation_key not in self._relation_cache:
                    self._relation_cache.add(relation_key)
                    new_relations.append(rel_dict)
        
        # Dependency-matcher-based relations
        for match_id, token_ids in dep_matches:
            relation_label = self.nlp_pipe.vocab.strings[match_id]
            ent1 = doc[token_ids[0]]
            ent2 = doc[token_ids[-1]]
            
            if __name__ == "__main__":
                print(f"{ent1.text} -[{relation_label}]-> {ent2.text}\n*******")
            
            rel_dict = {
                "ent1": ent1.text.strip().lower(),
                "relation": relation_label,
                "ent2": ent2.text.strip().lower(),
                **article_metadata
            }
            
            relation_key = (
                rel_dict["ent1"],
                rel_dict["relation"],
                rel_dict["ent2"],
                rel_dict.get("pmid", ""),
                rel_dict.get("pmcid", "")
            )
            
            if relation_key not in self._relation_cache:
                self._relation_cache.add(relation_key)
                new_relations.append(rel_dict)
        
        self.relations.extend(new_relations)
        logging.info(f"NLP: Added {len(new_relations)} new unique relations")
        
        return self
    
    def process_articles_batch(self, articles: List[Dict]) -> 'OptimizedNLP':
        """Process multiple articles efficiently."""
        logging.info(f"NLP: Processing batch of {len(articles)} articles")
        
        for article in articles:
            text = article.get('text', '')
            metadata = {k: v for k, v in article.items() if k != 'text'}
            
            if text:
                self.extract_and_normalize_entities(text, metadata)
                self.extract_relations(text, metadata)
        
        return self
    
    def generate_entities_csv(self, file_path: str):
        """Generate entities CSV with optimized DataFrame creation."""
        if not self.entities:
            logging.warning("NLP: No Entities In self.entities. Make Sure To Extract Them First.")
            print("no entities found, extract first.")
            df = pd.DataFrame(data=[{"entity": "", "label": ""}])
        else: 
            df = pd.DataFrame(data=self.entities)
        
        try:
            df.to_csv(file_path, index=False)
            logging.info(f"NLP: Entities Saved To {file_path}")
            print(f"entities saved to {file_path}")
        except Exception as e:
            logging.error(f"NLP: Failed To Save Entities As CSV: Error: {e}")
            print("error saving entities to csv.")
        
        return self
    
    def generate_relations_csv(self, file_path: str):
        """Generate relations CSV with optimized DataFrame creation."""
        if not self.relations:
            logging.warning("NLP: No Relations In self.relations. Make Sure To Extract Them First.")
            print("no relations found, extract first.")
            df = pd.DataFrame(data=[{"ent1": "", "relation": "", "ent2": ""}])
        else: 
            df = pd.DataFrame(data=self.relations)
        
        try:
            df.to_csv(file_path, index=False)
            logging.info(f"NLP: Relations Saved To {file_path}")
            print(f"relations saved to {file_path}")
        except Exception as e:
            logging.error(f"NLP: Failed To Save Relations As CSV: Error: {e}")
            print("error saving relations to csv.")
        
        return self
    
    def get_statistics(self) -> Dict:
        """Get processing statistics."""
        return {
            "total_entities": len(self.entities),
            "total_relations": len(self.relations),
            "cached_normalizations": len(self._normalization_cache),
            "unique_entity_texts": len(self._entity_cache),
            "unique_relations": len(self._relation_cache)
        }
    
    def __del__(self):
        """Save cache when object is destroyed."""
        if hasattr(self, '_normalization_cache') and self._normalization_cache:
            self._save_cache()


# Maintain backward compatibility
NLP = OptimizedNLP

# Keep the original main block for testing
if __name__ == "__main__": 
    normalizer = UMLSNormalizer()
    nlp = OptimizedNLP(normalizer=normalizer, max_workers=2, batch_size=10) 
    print("Entities recognized by ner_bionlp13cg_md model:")
    print(nlp.nlp_pipe.get_pipe("ner").labels)
    
    if not nlp.entities: 
        print("no entities, make sure to extract them.")
    elif not nlp.relations: 
        print("no relations, make sure to extract them.")
    else: 
        print(nlp.entities, nlp.relations, sep="\n *** \n")
    
    # Print statistics
    stats = nlp.get_statistics()
    print(f"Statistics: {stats}")