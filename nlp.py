import spacy
from spacy.matcher import Matcher, DependencyMatcher

from config.nlp_config import MATCHER_PATTERNS, DEPENDENCY_MATCHER_PATTERNS



nlp_pipeline = spacy.load("en_ner_bionlp13cg_md")
matcher = Matcher(nlp_pipeline.vocab)
dep_matcher = DependencyMatcher(nlp_pipeline.vocab)

for relation, patterns in MATCHER_PATTERNS.items():
    matcher.add(key=relation, patterns = patterns)

for relation, patterns in DEPENDENCY_MATCHER_PATTERNS.items():
    dep_matcher.add(key=relation, patterns= patterns)


text = 'Prostate cancer often involves mutations in the BRCA2 gene, which regulates DNA repair. The mutated gene produces abnormal proteins that affect cellular components in the prostate gland. Gastric cancer originates from the stomach lining and is associated with Helicobacter pylori infection. Treatments containing chemotherapy agents aim to cure pathological formations caused by these cancers. Biomarkers found in bodily fluids serve as indicators for early detection of both prostate and stomach cancers. Furthermore, prostate tumors are often located in specific anatomical systems and tissues, complicating treatment strategies.'

doc = nlp_pipeline(text)
matches = matcher(doc)
dep_matches = dep_matcher(doc)
print(len(matches), len(dep_matches))

def ner_and_er(text):
    
    for ent in doc.ents:
        print("token: ", ent.text, ", entity: ", ent.label_)

    for match_id, start, end in matches:
        string_id = nlp_pipeline.vocab.strings[match_id]
        span = doc[start:end]
        print("MATCHER:", match_id, string_id, start, end, span.text)

    for match_id, node_dict in dep_matches:
        string_id = nlp_pipeline.vocab.strings[match_id]
        print("DEPENDENCYMATCHER:", string_id)
        for node_id, token_idx in node_dict.items():
            print(f"  {node_id}: {doc[token_idx].text}")
        token_indices = list(node_dict.values())
        span = doc[min(token_indices) : max(token_indices) + 1]
        print("  Span:", span.text)


#ner_and_er(text=text)