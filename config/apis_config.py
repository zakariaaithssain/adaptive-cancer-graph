#PUBMED AND PUBMED CENTRAL CONFIG
PM_API_SLEEP_TIME = {"with_key" : 0.11,  #with key we have 10requests/second
                  
                  "without_key" : 0.34 #without key we have 3requests/second
                  } 



#the medline[sb] filter is to get data from the Medline Subset of PubMed that 
# contains more high quality data
PM_QUERIES = {
    
    "cancer_gene_regulation": '''
    ("Neoplasms"[MeSH] OR "cancer" OR "carcinoma" OR "tumor" OR "malignancy") AND 
    (
        "Gene Expression Regulation, Neoplastic"[MeSH] OR "Oncogenes"[MeSH] OR "Genes, Tumor Suppressor"[MeSH] OR
        "gene expression" OR "protein expression" OR "transcriptional regulation" OR "epigenetic regulation" OR
        "upregulates" OR "downregulates" OR "overexpressed" OR "silenced" OR "activates" OR "inhibits" OR
        "TP53" OR "KRAS" OR "MYC" OR "PTEN" OR "RB1" OR "BRCA1" OR "BRCA2" OR "EGFR" OR "PIK3CA"
    )
    AND medline[sb] AND "free full text"[sb]
    AND ("2020"[Date - Publication] : "2024"[Date - Publication])
    ''',
    
    "cancer_cell_signaling": '''
    ("Neoplasms"[MeSH] OR "cancer cells" OR "tumor cells" OR "malignant cells") AND
    (
        "Signal Transduction"[MeSH] OR "Cell Communication"[MeSH] OR "Protein Binding"[MeSH] OR
        "binds to" OR "interacts with" OR "phosphorylates" OR "ubiquitinates" OR "methylates" OR
        "pathway" OR "cascade" OR "signaling network" OR "protein complex" OR "receptor binding" OR
        "kinase" OR "phosphatase" OR "transcription factor" OR "growth factor" OR "cytokine"
    )
    AND medline[sb] AND "free full text"[sb]
    AND ("2020"[Date - Publication] : "2024"[Date - Publication])
    ''',
    
    "cancer_microenvironment": '''
    ("Neoplasms"[MeSH] OR "cancer" OR "tumor") AND
    (
        "Tumor Microenvironment"[MeSH] OR "Neoplastic Stem Cells"[MeSH] OR "Stromal Cells"[MeSH] OR
        "tumor microenvironment" OR "cancer stem cells" OR "fibroblasts" OR "endothelial cells" OR
        "immune cells" OR "macrophages" OR "T cells" OR "extracellular matrix" OR "angiogenesis" OR
        "invasion" OR "metastasis" OR "cell migration" OR "epithelial mesenchymal transition" OR
        "secreted by" OR "produces" OR "contains" OR "surrounds" OR "located in"
    )
    AND medline[sb] AND "free full text"[sb]
    AND ("2020"[Date - Publication] : "2024"[Date - Publication])
    ''',
    
    "cancer_metabolism": '''
    ("Neoplasms"[MeSH] OR "cancer metabolism" OR "tumor metabolism") AND
    (
        "Cell Metabolism"[MeSH] OR "Amino Acids"[MeSH] OR "Metabolic Networks and Pathways"[MeSH] OR
        "glucose metabolism" OR "amino acid metabolism" OR "fatty acid metabolism" OR "metabolite" OR
        "enzyme" OR "substrate" OR "product" OR "cofactor" OR "metabolic pathway" OR
        "glycolysis" OR "oxidative phosphorylation" OR "glutaminolysis" OR "Warburg effect" OR
        "produces" OR "converts" OR "catalyzes" OR "metabolizes" OR "component of"
    )
    AND medline[sb] AND "free full text"[sb]
    AND ("2020"[Date - Publication] : "2024"[Date - Publication])
    ''',
    
    "cancer_biomarkers": '''
    ("Neoplasms"[MeSH] OR "cancer" OR "carcinoma" OR "sarcoma") AND
    (
        "Biomarkers, Tumor"[MeSH] OR "Biological Markers"[MeSH] OR "Neoplasm Proteins"[MeSH] OR
        "biomarker" OR "tumor marker" OR "diagnostic marker" OR "prognostic marker" OR "predictive marker" OR
        "expressed in" OR "elevated in" OR "detected in" OR "associated with" OR "correlates with" OR
        "serum" OR "plasma" OR "tissue" OR "biopsy" OR "circulating" OR "secreted" OR
        "biomarker for" OR "indicator of" OR "predictive of"
    )
    AND medline[sb] AND "free full text"[sb]
    AND ("2020"[Date - Publication] : "2024"[Date - Publication])
    ''',
    
    "cancer_drug_therapy": '''
    ("Neoplasms"[MeSH] OR "cancer therapy" OR "anticancer") AND
    (
        "Antineoplastic Agents"[MeSH] OR "Drug Therapy"[MeSH] OR "Molecular Targeted Therapy"[MeSH] OR
        "chemotherapy" OR "targeted therapy" OR "immunotherapy" OR "drug resistance" OR "cytotoxic" OR
        "therapeutic target" OR "drug binding" OR "mechanism of action" OR "treats" OR "inhibits" OR
        "blocks" OR "targets" OR "binds to" OR "toxic to" OR "damages" OR "affects" OR
        "sensitivity" OR "resistance" OR "efficacy" OR "pharmacokinetics"
    )
    AND medline[sb] AND "free full text"[sb]
    AND ("2020"[Date - Publication] : "2024"[Date - Publication])
    ''',
    
    "cancer_mutations": '''
    ("Neoplasms"[MeSH] OR "cancer" OR "tumor") AND
    (
        "Mutation"[MeSH] OR "DNA Mutational Analysis"[MeSH] OR "Chromosomal Instability"[MeSH] OR
        "somatic mutation" OR "germline mutation" OR "point mutation" OR "deletion" OR "insertion" OR
        "translocation" OR "amplification" OR "loss of heterozygosity" OR "chromosomal aberration" OR
        "mutated in" OR "variant" OR "polymorphism" OR "genetic alteration" OR "genomic instability" OR
        "oncogenic mutation" OR "driver mutation" OR "passenger mutation" OR "frameshift" OR "nonsense"
    )
    AND medline[sb] AND "free full text"[sb]
    AND ("2020"[Date - Publication] : "2024"[Date - Publication])
    ''',
    
    "cancer_development": '''
    ("Neoplasms"[MeSH] OR "carcinogenesis" OR "tumorigenesis") AND
    (
        "Carcinogenesis"[MeSH] OR "Cell Transformation, Neoplastic"[MeSH] OR "Neoplastic Processes"[MeSH] OR
        "tumor initiation" OR "tumor progression" OR "malignant transformation" OR "oncogenesis" OR
        "cell proliferation" OR "apoptosis" OR "cell cycle" OR "DNA repair" OR "genomic instability" OR
        "originates from" OR "develops into" OR "arises from" OR "transforms into" OR "progresses to" OR
        "precursor" OR "dysplasia" OR "hyperplasia" OR "metaplasia" OR "differentiation"
    )
    AND medline[sb] AND "free full text"[sb]
    AND ("2020"[Date - Publication] : "2024"[Date - Publication])
    '''
}


#UMLS CONFIGURATION
#we are allowed to do 20req/s, which means that we should wait at least 0.05s/req
UMLS_API_SLEEP_TIME = 0.06 






