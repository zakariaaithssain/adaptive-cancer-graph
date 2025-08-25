import pandas as pd
import spacy
import logging
import pickle
import hashlib
import warnings

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from spacy.matcher import Matcher, DependencyMatcher

from modules.umls_api import UMLSNormalizer
from config.nlp_config import MATCHER_PATTERNS, DEPENDENCY_MATCHER_PATTERNS
from config.nlp_config import GENERIC_ENTITIES

class StreamingOptimizedNLP:
    def __init__(self, normalizer: UMLSNormalizer, 
                 entities_output_path: str,
                 relations_output_path: str,
                 batch_size: int = 50, 
                 max_workers: int = 8,
                 buffer_size: int = 1000):

       #supressing a future warning coming from inside spacy load 
        warnings.filterwarnings("ignore", category=FutureWarning, module="spacy")
        logging.info("NLP: Loading NER Model...")
        print("loading ner model...")
        self.nlp_pipe = spacy.load("en_ner_bionlp13cg_md") 
        self.nlp_pipe.add_pipe("merge_entities", after="ner")
        
        # Initialize matchers with model vocab
        self.matcher = Matcher(self.nlp_pipe.vocab)
        self.dep_matcher = DependencyMatcher(self.nlp_pipe.vocab)
        
        # Initialize the normalizer
        self.normalizer = normalizer
        
        # Performance optimization settings
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.buffer_size = buffer_size
        
        # Output paths for streaming
        self.entities_output_path = entities_output_path
        self.relations_output_path = relations_output_path
        

        
        # Streaming buffers
        self._entities_buffer = []
        self._relations_buffer = []
        
        # Track if CSV headers have been written
        self._entities_header_written = False
        self._relations_header_written = False
        
        # Caching and deduplication
        self._normalization_cache = {}
        self._entity_cache = set()
        self._relation_cache = set()

        # Load old cache to make sure we build cache each time we run the ETL and not losing old one.
        self._load_cache()
        
        # Initialize streaming CSV files

        self._initialize_streaming_files()
        
        # Add patterns to matchers
        for label, patterns in MATCHER_PATTERNS.items():
            self.matcher.add(label, patterns)

        for label, patterns in DEPENDENCY_MATCHER_PATTERNS.items():
            self.dep_matcher.add(label, patterns)



    
    def _initialize_streaming_files(self):
        """Initialize CSV files for streaming output."""
        # Ensure directory exists
        Path(self.entities_output_path).parent.mkdir(parents=True, exist_ok=True)
        # Create/truncate the file
        with open(self.entities_output_path, 'w', newline='', encoding='utf-8'):
            pass  # Just create/truncate the file to 0 (empty it)
        
        Path(self.relations_output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.relations_output_path, 'w', newline='', encoding='utf-8'):
            pass
    



    def _stream_entities_to_csv(self, entities_batch: list[dict]):
        """Stream a batch of entities directly to CSV."""
        if not entities_batch:
            return
        
        try:
            # Convert to DataFrame for easy CSV writing
            df = pd.DataFrame(entities_batch)
            
            # Write header only once
            write_header = not self._entities_header_written
            mode = 'w' if write_header else 'a'
            
            df.to_csv(self.entities_output_path, mode=mode, header=write_header, index=False)
            
            if write_header:
                self._entities_header_written = True
            
            logging.debug(f"NLP: Streamed {len(entities_batch)} entities to CSV")
            
        except Exception as e:
            logging.error(f"NLP: Failed to stream entities to CSV: {e}")



    
    def _stream_relations_to_csv(self, relations_batch: list[dict]):
        """Stream a batch of relations directly to CSV."""
        if not relations_batch:
            return
        
        try:
            df = pd.DataFrame(relations_batch)
            
            write_header = not self._relations_header_written
            mode = 'w' if write_header else 'a'
            
            df.to_csv(self.relations_output_path, mode=mode, header=write_header, index=False)
            
            if write_header:
                self._relations_header_written = True
            
            logging.debug(f"NLP: Streamed {len(relations_batch)} relations to CSV")
            
        except Exception as e:
            logging.error(f"NLP: Failed to stream relations to CSV: {e}")



    
    def _flush_entities_buffer(self, force: bool = False):
        """Flush entities buffer to CSV when it reaches buffer_size or when force=True."""
        if (len(self._entities_buffer) >= self.buffer_size or force) and self._entities_buffer:
            self._stream_entities_to_csv(self._entities_buffer)
            
            self._entities_buffer.clear()
    



    def _flush_relations_buffer(self, force: bool = False):
        """Flush relations buffer to CSV when it reaches buffer_size or when force=True."""
        if (len(self._relations_buffer) >= self.buffer_size or force) and self._relations_buffer:
            self._stream_relations_to_csv(self._relations_buffer)
            
            self._relations_buffer.clear()



    
    def _generate_cache_key(self, text: str) -> str:
        """Generate a MD5 hash key (id) for caching normalized entities."""
        return hashlib.md5(text.lower().strip().encode()).hexdigest()
    
    def _load_cache(self):
        """Load normalization cache from disk if it exists."""
        try:
            with open('cache/normalization_cache.pkl', 'rb') as f:
                self._normalization_cache = pickle.load(f)
            logging.info(f"NLP: Loaded {len(self._normalization_cache)} cached normalizations.")
        except FileNotFoundError:
            logging.info("NLP: No existing cache found, starting fresh.")
    
    def _save_cache(self):
        """Save normalization cache to disk. Cache grows each time we run the pipeline,
        because in __init__ we call _load_cache to re-add old cache to the new one"""
        try:
            with open('cache/normalization_cache.pkl', 'wb') as f:
                pickle.dump(self._normalization_cache, f)
            logging.info(f"NLP: Saved {len(self._normalization_cache)} normalizations to cache")
        except Exception as e:
            logging.error(f"NLP: Failed to save normalizations to cache: {e}")
    
    def _should_normalize(self, text: str) -> bool:
        """Determine if entity should be normalized (skip very short/common ones)."""
        text = text.strip().lower()
        skip_patterns = GENERIC_ENTITIES | {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return len(text) >= 1 and text not in skip_patterns
    
    def _batch_normalize_entities(self, entity_texts: list[str]) -> dict[str, dict]:
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
                results[text] = {"cui": "", "normalized_name": "", "normalization_source": ""}
        
        if not to_normalize:
            return results
        
        #now we use the API to normalize entities that aren't in cache
        logging.info(f"NLP: Normalizing {len(to_normalize)} new entities via UMLS API")

        for i in range(0, len(to_normalize), self.batch_size):
            batch = to_normalize[i:i + self.batch_size]
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_text : dict = {
                    executor.submit(self.normalizer.normalize, text) #key (a Future obj)
                    :
                    text for text in batch # value (text)
                }
                
#get the normalization as soon as it's done (in the order they finish, not in submission order)
                for future in as_completed(future_to_text.keys()): 
                    text = future_to_text[future]
                    try:
                        normalization_result = future.result()
                        cache_key = self._generate_cache_key(text)
                        
                        self._normalization_cache[cache_key] = normalization_result
                        results[text] = normalization_result
                        
                    except Exception:
                        results[text] = {"cui": "", "normalized_name": "", "normalization_source": ""}
            
        #save cache to disk after each new 100 normalizations 
        if len(self._normalization_cache) % 100 == 0:
            self._save_cache()
        
        return results
    


    
    def extract_and_normalize_entities(self, text: str, article_metadata: dict):
        """Extract recognized entities from text with 
        optimized normalization and streaming."""
        doc = self.nlp_pipe(text)
        
        if not doc.ents:
            return self
        
        entity_texts_to_normalize = set()
        extracted_entities = []
        
        for ent in doc.ents:
            lemma = ent.lemma_.strip().lower()
            #we have nothing to do with generic entities (e.g. cancer, tumor...)
            if lemma not in GENERIC_ENTITIES:
                if __name__ == "__main__": 
                    print(f"entity: {lemma} --- label: {ent.label_}\n ******* ")
                
                
                entity_dict = {
                    "text": lemma,
                    "label": ent.label_,
                    **article_metadata
                }
                
                extracted_entities.append(entity_dict)
                entity_texts_to_normalize.add(lemma)
        
        # Batch normalize all unique entity texts
        normalization_results = self._batch_normalize_entities(list(entity_texts_to_normalize))
        
        # Apply normalization results to entities
        final_entities = []
        for entity_dict in extracted_entities:
            original_text = None
            for ent in doc.ents:
                if ent.lemma_.strip().lower() == entity_dict["text"]:
                    original_text = ent.lemma_.strip()
                    break
            
            if original_text and original_text in normalization_results:
                entity_dict.update(normalization_results[original_text])
            
            entity_key = (
                entity_dict["text"], 
                entity_dict["label"], 
                entity_dict.get("pmid", ""), 
                entity_dict.get("pmcid", "")
            )
            
            if entity_key not in self._entity_cache:
                self._entity_cache.add(entity_key)
                final_entities.append(entity_dict)
        
        # Add to buffer instead of directly to entities list
        self._entities_buffer.extend(final_entities)
        
        # Flush buffer if it's full
        self._flush_entities_buffer()
        
        logging.info(f"NLP: Added {len(final_entities)} new unique entities to buffer")
        
        return self
    


    
    def extract_relations(self, text: str, article_metadata: dict):
        """Extract relations with optimized deduplication and streaming."""
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
                    print(f"{ent1.lemma_} -[{relation_label}]-> {ent2.lemma_}\n*******")
                
                rel_dict = {
                    "ent1": ent1.lemma_.strip().lower(),
                    "relation": relation_label,
                    "ent2": ent2.lemma_.strip().lower(),
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
        
        # Dependency-matcher-based relations
        for match_id, token_ids in dep_matches:
            relation_label = self.nlp_pipe.vocab.strings[match_id]
            ent1 = doc[token_ids[0]]
            ent2 = doc[token_ids[-1]]
            
            if __name__ == "__main__":
                print(f"{ent1.lemma_} -[{relation_label}]-> {ent2.lemma_}\n*******")
            
            rel_dict = {
                "ent1": ent1.lemma_.strip().lower(),
                "relation": relation_label,
                "ent2": ent2.lemma_.strip().lower(),
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
        
        # Add to buffer instead of directly to relations list
        self._relations_buffer.extend(new_relations)
        
        # Flush buffer if it's full
        self._flush_relations_buffer()
        
        logging.info(f"NLP: Added {len(new_relations)} new unique relations to buffer")
        
        return self
    


    
    def process_articles_batch(self, articles: list[dict]) -> 'StreamingOptimizedNLP':
        """Process multiple articles efficiently with streaming."""
        logging.info(f"NLP: Processing batch of {len(articles)} articles")
        
        for article in articles:
            text = article.get('text', '')
            metadata = {k: v for k, v in article.items() if k != 'text'}
            
            if text:
                self.extract_and_normalize_entities(text, metadata)
                self.extract_relations(text, metadata)
        
        # Force flush buffers after processing batch
        self.flush_all_buffers()
        
        return self
    



    def flush_all_buffers(self):
        """Force flush all buffers to CSV files."""
        self._flush_entities_buffer(force=True)
        self._flush_relations_buffer(force=True)
        logging.info("NLP: Flushed all buffers to CSV files")
    




    def get_info(self) -> dict:
        """Get processing statistics."""
        return {
            "total_entities": len(self.entities) + len(self._entities_buffer),
            "total_relations": len(self.relations) + len(self._relations_buffer),
            "cached_normalizations": len(self._normalization_cache),
            "unique_entity_texts": len(self._entity_cache),
            "unique_relations": len(self._relation_cache),
            "entities_in_buffer": len(self._entities_buffer),
            "relations_in_buffer": len(self._relations_buffer),
        }
    



    def __del__(self):
        """Save cache and flush buffers when object is destroyed."""
        if hasattr(self, '_normalization_cache') and self._normalization_cache:
            self._save_cache()
        
        if hasattr(self, '_entities_buffer') or hasattr(self, '_relations_buffer'):
            self.flush_all_buffers()


