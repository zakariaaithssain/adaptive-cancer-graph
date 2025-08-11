import spacy

# Load the model, disabling unnecessary components
nlp = spacy.load("en_ner_bionlp13cg_md", disable=['tagger', 'attribute_ruler', 'lemmatizer', 'parser'])

text = ("Prostate cancer is one of the most common cancers in men worldwide. "
        "Mutations in the BRCA2 gene have been linked to a higher risk of developing aggressive prostate tumors. "
        "Elevated levels of PSA (prostate-specific antigen) are often used as a biomarker for early detection. "
        "Treatments such as radical prostatectomy and androgen deprivation therapy (ADT) are standard approaches. "
        "Recent studies suggest that exposure to environmental toxins may increase the risk, "
        "while genetic factors like alterations in the TP53 gene also play a crucial role.")

doc = nlp(text)

for ent in doc.ents:
    print(f"Entity: {ent.text}, Label: {ent.label_}")
    
