# -------------------------------
# TOKEN-BASED MATCHER PATTERNS
# -------------------------------
MATCHER_PATTERNS = {
    "PRODUCES": [
        # Original pattern
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LEMMA": "produce"}, {"OP": "*"}, {"ENT_TYPE": "AMINO_ACID"}],
        # Enhanced patterns
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LEMMA": {"IN": ["generate", "synthesize", "create", "make"]}}, {"OP": "*"}, {"ENT_TYPE": "AMINO_ACID"}],
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LEMMA": "code"}, {"LOWER": "for"}, {"OP": "*"}, {"ENT_TYPE": "AMINO_ACID"}],
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LEMMA": "encode"}, {"OP": "*"}, {"ENT_TYPE": "AMINO_ACID"}],
        # Cell/organism producing substances
        [{"ENT_TYPE": {"IN": ["CELL", "ORGAN"]}}, {"OP": "*"}, {"LEMMA": {"IN": ["produce", "secrete", "release"]}}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["ORGANISM_SUBSTANCE", "SIMPLE_CHEMICAL"]}}]
    ],
    "CONTAINS": [
        # Original pattern
        [{"ENT_TYPE": "AMINO_ACID"}, {"OP": "*"}, {"LEMMA": "contain"}, {"OP": "*"}, {"ENT_TYPE": "SIMPLE_CHEMICAL"}],
        # Enhanced patterns - more entity combinations
        [{"ENT_TYPE": {"IN": ["CELLULAR_COMPONENT", "ORGAN", "TISSUE"]}}, {"OP": "*"}, {"LEMMA": {"IN": ["contain", "include", "comprise", "harbor"]}}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["GENE_OR_GENE_PRODUCT", "SIMPLE_CHEMICAL", "CELL"]}}],
        [{"ENT_TYPE": "ORGANISM_SUBSTANCE"}, {"OP": "*"}, {"LEMMA": "contain"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["AMINO_ACID", "SIMPLE_CHEMICAL"]}}],
        # "rich in" pattern
        [{"ENT_TYPE": {"IN": ["CELL", "TISSUE", "ORGAN"]}}, {"OP": "*"}, {"LOWER": "rich"}, {"LOWER": "in"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["SIMPLE_CHEMICAL", "AMINO_ACID"]}}]
    ],
    "BINDS": [
        # Original pattern
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LEMMA": "bind"}, {"OP": "*"}, {"ENT_TYPE": "SIMPLE_CHEMICAL"}],
        # Enhanced patterns with more binding terms
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LEMMA": {"IN": ["interact", "associate", "complex"]}}, {"LOWER": "with"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["SIMPLE_CHEMICAL", "GENE_OR_GENE_PRODUCT"]}}],
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LOWER": "binding"}, {"LOWER": "to"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["SIMPLE_CHEMICAL", "GENE_OR_GENE_PRODUCT"]}}],
        # Bidirectional binding
        [{"ENT_TYPE": "SIMPLE_CHEMICAL"}, {"OP": "*"}, {"LEMMA": "bind"}, {"OP": "*"}, {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}],
        # Receptor-ligand binding
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LOWER": {"IN": ["receptor", "target"]}}, {"LOWER": "for"}, {"OP": "*"}, {"ENT_TYPE": "SIMPLE_CHEMICAL"}]
    ],
    "REGULATES": [
        # Original pattern
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LEMMA": "regulate"}, {"OP": "*"}, {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}],
        # Enhanced with more regulatory terms
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LEMMA": {"IN": ["control", "modulate", "influence"]}}, {"OP": "*"}, {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}],
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LEMMA": {"IN": ["upregulate", "downregulate", "activate", "inhibit", "suppress", "repress"]}}, {"OP": "*"}, {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}],
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LEMMA": {"IN": ["promote", "enhance", "stimulate", "induce"]}}, {"OP": "*"}, {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}],
        # Transcriptional regulation
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LOWER": "transcription"}, {"LOWER": "factor"}, {"LOWER": "for"}, {"OP": "*"}, {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}]
    ],
    "EXPRESSED_IN": [
        # Original pattern
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LEMMA": "express"}, {"OP": "*"}, {"ENT_TYPE": "CELL"}],
        # Enhanced with more expression terms and locations
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LEMMA": {"IN": ["express", "present", "detect", "find", "observe"]}}, {"LOWER": "in"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["CELL", "TISSUE", "ORGAN"]}}],
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LOWER": {"IN": ["overexpressed", "overexpression", "upregulated"]}}, {"LOWER": "in"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["CELL", "TISSUE", "CANCER"]}}],
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LOWER": {"IN": ["abundant", "enriched", "elevated"]}}, {"LOWER": "in"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["CELL", "TISSUE", "ORGAN"]}}],
        # Specific to cancer
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LOWER": {"IN": ["highly", "specifically"]}}, {"LEMMA": "express"}, {"LOWER": "in"}, {"OP": "*"}, {"ENT_TYPE": "CANCER"}]
    ],
    "MUTATED_IN": [
        # Original pattern
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LEMMA": "mutation"}, {"OP": "*"}, {"ENT_TYPE": "CANCER"}],
        # Enhanced with more mutation terms
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LEMMA": {"IN": ["mutate", "alter", "variant"]}}, {"LOWER": "in"}, {"OP": "*"}, {"ENT_TYPE": "CANCER"}],
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LOWER": {"IN": ["deletion", "amplification", "translocation", "rearrangement"]}}, {"LOWER": "in"}, {"OP": "*"}, {"ENT_TYPE": "CANCER"}],
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LOWER": {"IN": ["polymorphism", "variant", "allele"]}}, {"LOWER": "in"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["CANCER", "CELL"]}}],
        # Loss/gain patterns
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LOWER": {"IN": ["loss", "inactivation"]}}, {"LOWER": "in"}, {"OP": "*"}, {"ENT_TYPE": "CANCER"}],
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LOWER": {"IN": ["oncogenic", "driver"]}}, {"LEMMA": "mutation"}, {"LOWER": "in"}, {"OP": "*"}, {"ENT_TYPE": "CANCER"}]
    ],
    "PART_OF": [
        # Original pattern enhanced
        [{"ENT_TYPE": {"IN": ["CELL", "CELLULAR_COMPONENT", "TISSUE", "ORGAN", "MULTI_TISSUE_STRUCTURE", "ORGANISM_SUBDIVISION"]}},
         {"OP": "*"}, {"LOWER": "part"}, {"LOWER": "of"}, {"OP": "*"},
         {"ENT_TYPE": {"IN": ["TISSUE", "ORGAN", "MULTI_TISSUE_STRUCTURE", "ANATOMICAL_SYSTEM", "ORGANISM"]}}],
        # Additional structural relationships
        [{"ENT_TYPE": {"IN": ["CELLULAR_COMPONENT", "CELL"]}}, {"OP": "*"}, {"LOWER": {"IN": ["component", "element", "constituent"]}}, {"LOWER": "of"}, {"OP": "*"},
         {"ENT_TYPE": {"IN": ["CELL", "TISSUE", "ORGAN"]}}],
        [{"ENT_TYPE": {"IN": ["TISSUE", "ORGAN"]}}, {"OP": "*"}, {"LOWER": {"IN": ["within", "inside"]}}, {"OP": "*"},
         {"ENT_TYPE": {"IN": ["ORGAN", "MULTI_TISSUE_STRUCTURE", "ANATOMICAL_SYSTEM"]}}]
    ],
    "LOCATED_IN": [
        # Original pattern
        [{"ENT_TYPE": {"IN": ["CELL", "ORGAN"]}}, {"OP": "*"}, {"LOWER": "located"}, {"LOWER": "in"}, {"OP": "*"},
         {"ENT_TYPE": {"IN": ["ORGAN", "ORGANISM_SUBDIVISION", "MULTI_TISSUE_STRUCTURE"]}}],
        # Enhanced location patterns
        [{"ENT_TYPE": {"IN": ["GENE_OR_GENE_PRODUCT", "CELLULAR_COMPONENT"]}}, {"OP": "*"}, {"LOWER": {"IN": ["found", "present", "situated"]}}, {"LOWER": "in"}, {"OP": "*"},
         {"ENT_TYPE": {"IN": ["CELL", "CELLULAR_COMPONENT", "TISSUE", "ORGAN"]}}],
        [{"ENT_TYPE": {"IN": ["CELL", "TISSUE"]}}, {"OP": "*"}, {"LOWER": {"IN": ["within", "inside"]}}, {"OP": "*"},
         {"ENT_TYPE": {"IN": ["ORGAN", "ORGANISM_SUBDIVISION", "MULTI_TISSUE_STRUCTURE"]}}],
        # Subcellular localization
        [{"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, {"OP": "*"}, {"LOWER": {"IN": ["localized", "targeted"]}}, {"LOWER": "to"}, {"OP": "*"},
         {"ENT_TYPE": {"IN": ["CELLULAR_COMPONENT", "CELL"]}}]
    ],
    "ORIGIN_OF": [
        # Original pattern
        [{"ENT_TYPE": "CELL"}, {"OP": "*"}, {"LOWER": "origin"}, {"LOWER": "of"}, {"OP": "*"}, {"ENT_TYPE": "CANCER"}],
        # Enhanced origin patterns
        [{"ENT_TYPE": {"IN": ["CELL", "TISSUE"]}}, {"OP": "*"}, {"LOWER": {"IN": ["source", "precursor"]}}, {"LOWER": "of"}, {"OP": "*"}, {"ENT_TYPE": "CANCER"}],
        [{"ENT_TYPE": "CELL"}, {"OP": "*"}, {"LOWER": "gives"}, {"LOWER": "rise"}, {"LOWER": "to"}, {"OP": "*"}, {"ENT_TYPE": "CANCER"}]
    ],
    "CONTAINS_COMPONENT": [
        # Original pattern
        [{"ENT_TYPE": "CELLULAR_COMPONENT"}, {"OP": "*"}, {"LEMMA": "contain"}, {"OP": "*"}, {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}],
        # Enhanced with more components
        [{"ENT_TYPE": {"IN": ["CELLULAR_COMPONENT", "CELL", "ORGAN"]}}, {"OP": "*"}, {"LEMMA": {"IN": ["contain", "include", "comprise", "house"]}}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["GENE_OR_GENE_PRODUCT", "SIMPLE_CHEMICAL", "AMINO_ACID"]}}]
    ],
    "SURROUNDS": [
        # Original pattern
        [{"ENT_TYPE": "IMMATERIAL_ANATOMICAL_ENTITY"}, {"OP": "*"}, {"LEMMA": "surround"}, {"OP": "*"}, {"ENT_TYPE": "ORGAN"}],
        # Enhanced surrounding patterns
        [{"ENT_TYPE": {"IN": ["TISSUE", "CELLULAR_COMPONENT"]}}, {"OP": "*"}, {"LEMMA": {"IN": ["surround", "encircle", "enclose"]}}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["ORGAN", "CELL", "TISSUE"]}}]
    ],
    "DEVELOPS_INTO": [
        # Original pattern
        [{"ENT_TYPE": "DEVELOPING_ANATOMICAL_STRUCTURE"}, {"OP": "*"}, {"LEMMA": "develop"}, {"LOWER": "into"}, {"OP": "*"}, {"ENT_TYPE": "ORGAN"}],
        # Enhanced development patterns
        [{"ENT_TYPE": {"IN": ["DEVELOPING_ANATOMICAL_STRUCTURE", "CELL"]}}, {"OP": "*"}, {"LEMMA": {"IN": ["differentiate", "mature", "transform"]}}, {"LOWER": "into"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["ORGAN", "TISSUE", "CELL"]}}],
        [{"ENT_TYPE": "CELL"}, {"OP": "*"}, {"LOWER": "becomes"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["CELL", "TISSUE"]}}]
    ],
    "ORIGINATES_FROM": [
        # Original pattern
        [{"ENT_TYPE": "CANCER"}, {"OP": "*"}, {"LEMMA": "originate"}, {"LOWER": "in"}, {"OP": "*"}, {"ENT_TYPE": "ORGAN"}],
        # Enhanced with more origin terms
        [{"ENT_TYPE": "CANCER"}, {"OP": "*"}, {"LEMMA": {"IN": ["originate", "derive", "stem"]}}, {"LOWER": "from"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["ORGAN", "TISSUE", "CELL"]}}],
        [{"ENT_TYPE": "CANCER"}, {"OP": "*"}, {"LOWER": {"IN": ["primary", "located"]}}, {"LOWER": "in"}, {"OP": "*"}, {"ENT_TYPE": "ORGAN"}]
    ],
    "ARISES_FROM": [
        # Original pattern
        [{"ENT_TYPE": "CANCER"}, {"OP": "*"}, {"LEMMA": "arise"}, {"LOWER": "from"}, {"OP": "*"}, {"ENT_TYPE": "CELL"}],
        # Enhanced with more arising terms
        [{"ENT_TYPE": "CANCER"}, {"OP": "*"}, {"LEMMA": {"IN": ["arise", "emerge", "develop"]}}, {"LOWER": "from"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["CELL", "TISSUE"]}}],
        [{"ENT_TYPE": "PATHOLOGICAL_FORMATION"}, {"OP": "*"}, {"LEMMA": "arise"}, {"LOWER": "from"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["CELL", "TISSUE"]}}]
    ],
    "AFFECTS": [
        # Original pattern
        [{"ENT_TYPE": "PATHOLOGICAL_FORMATION"}, {"OP": "*"}, {"LEMMA": "affect"}, {"OP": "*"}, {"ENT_TYPE": "ORGAN"}],
        # Enhanced with more effect terms
        [{"ENT_TYPE": {"IN": ["PATHOLOGICAL_FORMATION", "CANCER"]}}, {"OP": "*"}, {"LEMMA": {"IN": ["affect", "impact", "influence", "involve"]}}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["ORGAN", "TISSUE", "CELL"]}}],
        [{"ENT_TYPE": "SIMPLE_CHEMICAL"}, {"OP": "*"}, {"LEMMA": {"IN": ["affect", "target", "act"]}}, {"LOWER": "on"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["CELL", "ORGAN", "TISSUE"]}}]
    ],
    "ASSOCIATED_WITH": [
        # Original pattern
        [{"ENT_TYPE": "PATHOLOGICAL_FORMATION"}, {"OP": "*"}, {"LOWER": "associate"}, {"LOWER": "with"}, {"OP": "*"}, {"ENT_TYPE": "CANCER"}],
        # Enhanced association patterns
        [{"ENT_TYPE": {"IN": ["GENE_OR_GENE_PRODUCT", "SIMPLE_CHEMICAL"]}}, {"OP": "*"}, {"LEMMA": {"IN": ["associate", "correlate", "link"]}}, {"LOWER": "with"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["CANCER", "PATHOLOGICAL_FORMATION"]}}],
        [{"ENT_TYPE": {"IN": ["PATHOLOGICAL_FORMATION", "CANCER"]}}, {"OP": "*"}, {"LOWER": {"IN": ["related", "connected"]}}, {"LOWER": "to"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["GENE_OR_GENE_PRODUCT", "SIMPLE_CHEMICAL"]}}]
    ],
    "DAMAGES": [
        # Original pattern
        [{"ENT_TYPE": "PATHOLOGICAL_FORMATION"}, {"OP": "*"}, {"LEMMA": "damage"}, {"OP": "*"}, {"ENT_TYPE": "TISSUE"}],
        # Enhanced damage patterns
        [{"ENT_TYPE": {"IN": ["PATHOLOGICAL_FORMATION", "SIMPLE_CHEMICAL"]}}, {"OP": "*"}, {"LEMMA": {"IN": ["damage", "harm", "injure", "destroy"]}}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["TISSUE", "ORGAN", "CELL"]}}],
        [{"ENT_TYPE": {"IN": ["PATHOLOGICAL_FORMATION", "CANCER"]}}, {"OP": "*"}, {"LEMMA": {"IN": ["invade", "metastasize"]}}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["TISSUE", "ORGAN"]}}]
    ],
    "BIOMARKER_FOR": [
        # Original pattern
        [{"ENT_TYPE": "ORGANISM_SUBSTANCE"}, {"OP": "*"}, {"LOWER": "biomarker"}, {"LOWER": "for"}, {"OP": "*"}, {"ENT_TYPE": "CANCER"}],
        # Enhanced biomarker patterns
        [{"ENT_TYPE": {"IN": ["GENE_OR_GENE_PRODUCT", "ORGANISM_SUBSTANCE", "SIMPLE_CHEMICAL"]}}, {"OP": "*"}, {"LOWER": {"IN": ["biomarker", "marker", "indicator"]}}, {"LOWER": "for"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["CANCER", "PATHOLOGICAL_FORMATION"]}}],
        [{"ENT_TYPE": {"IN": ["GENE_OR_GENE_PRODUCT", "ORGANISM_SUBSTANCE"]}}, {"OP": "*"}, {"LOWER": {"IN": ["diagnostic", "prognostic", "predictive"]}}, {"LOWER": {"IN": ["marker", "biomarker"]}}, {"LOWER": "for"}, {"OP": "*"}, {"ENT_TYPE": "CANCER"}],
        [{"ENT_TYPE": {"IN": ["GENE_OR_GENE_PRODUCT", "ORGANISM_SUBSTANCE"]}}, {"OP": "*"}, {"LOWER": {"IN": ["elevated", "increased", "overexpressed"]}}, {"LOWER": "in"}, {"OP": "*"}, {"ENT_TYPE": "CANCER"}]
    ],
    "TOXIC_TO": [
        # Original pattern
        [{"ENT_TYPE": "SIMPLE_CHEMICAL"}, {"OP": "*"}, {"LOWER": "toxic"}, {"LOWER": "to"}, {"OP": "*"}, {"ENT_TYPE": "CELL"}],
        # Enhanced toxicity patterns
        [{"ENT_TYPE": "SIMPLE_CHEMICAL"}, {"OP": "*"}, {"LOWER": {"IN": ["toxic", "harmful", "cytotoxic", "poisonous"]}}, {"LOWER": "to"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["CELL", "TISSUE", "ORGAN"]}}],
        [{"ENT_TYPE": "SIMPLE_CHEMICAL"}, {"OP": "*"}, {"LEMMA": {"IN": ["kill", "destroy"]}}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["CELL", "CANCER"]}}]
    ],
    "COMPONENT_OF": [
        # Original pattern
        [{"ENT_TYPE": "SIMPLE_CHEMICAL"}, {"OP": "*"}, {"LOWER": "component"}, {"LOWER": "of"}, {"OP": "*"}, {"ENT_TYPE": "ORGANISM_SUBSTANCE"}],
        # Enhanced component patterns
        [{"ENT_TYPE": {"IN": ["SIMPLE_CHEMICAL", "AMINO_ACID", "GENE_OR_GENE_PRODUCT"]}}, {"OP": "*"}, {"LOWER": {"IN": ["component", "constituent", "element", "part"]}}, {"LOWER": "of"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["ORGANISM_SUBSTANCE", "CELLULAR_COMPONENT", "CELL"]}}]
    ],
    "SECRETED_BY": [
        # Original pattern
        [{"ENT_TYPE": "ORGANISM_SUBSTANCE"}, {"OP": "*"}, {"LOWER": "secret"}, {"LOWER": "by"}, {"OP": "*"}, {"ENT_TYPE": "ORGAN"}],
        # Enhanced secretion patterns
        [{"ENT_TYPE": {"IN": ["ORGANISM_SUBSTANCE", "SIMPLE_CHEMICAL"]}}, {"OP": "*"}, {"LEMMA": {"IN": ["secrete", "release", "produce", "excrete"]}}, {"LOWER": "by"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["ORGAN", "CELL", "TISSUE"]}}],
        # Passive forms
        [{"ENT_TYPE": {"IN": ["ORGANISM_SUBSTANCE", "SIMPLE_CHEMICAL"]}}, {"OP": "*"}, {"LEMMA": {"IN": ["secreted", "released", "produced"]}}, {"LOWER": "by"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["ORGAN", "CELL", "TISSUE"]}}]
    ],
    "TREATS": [
        # Original pattern
        [{"ENT_TYPE": "SIMPLE_CHEMICAL"}, {"OP": "*"}, {"LEMMA": "treat"}, {"OP": "*"}, {"ENT_TYPE": "PATHOLOGICAL_FORMATION"}],
        # Enhanced treatment patterns
        [{"ENT_TYPE": "SIMPLE_CHEMICAL"}, {"OP": "*"}, {"LEMMA": {"IN": ["treat", "cure", "heal", "therapy"]}}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["PATHOLOGICAL_FORMATION", "CANCER"]}}],
        [{"ENT_TYPE": "SIMPLE_CHEMICAL"}, {"OP": "*"}, {"LOWER": {"IN": ["effective", "used"]}}, {"LOWER": {"IN": ["against", "for"]}}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["CANCER", "PATHOLOGICAL_FORMATION"]}}],
        [{"ENT_TYPE": "SIMPLE_CHEMICAL"}, {"OP": "*"}, {"LOWER": {"IN": ["drug", "therapy", "treatment"]}}, {"LOWER": "for"}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["CANCER", "PATHOLOGICAL_FORMATION"]}}],
        # Inhibition patterns
        [{"ENT_TYPE": "SIMPLE_CHEMICAL"}, {"OP": "*"}, {"LEMMA": {"IN": ["inhibit", "block", "suppress"]}}, {"OP": "*"}, {"ENT_TYPE": {"IN": ["CANCER", "PATHOLOGICAL_FORMATION", "GENE_OR_GENE_PRODUCT"]}}]
    ]
}

# -------------------------------
# ENHANCED DEPENDENCY MATCHER PATTERNS
# -------------------------------
DEPENDENCY_MATCHER_PATTERNS = {
    "PRODUCES": [
        # Original pattern
        [
            {"RIGHT_ID": "gene", "RIGHT_ATTRS": {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": "produce"}, "LEFT_ID": "gene", "REL_OP": ">"},
            {"RIGHT_ID": "product", "RIGHT_ATTRS": {"ENT_TYPE": "AMINO_ACID"}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Enhanced with more production verbs
        [
            {"RIGHT_ID": "gene", "RIGHT_ATTRS": {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["generate", "synthesize", "create", "encode"]}}, "LEFT_ID": "gene", "REL_OP": ">"},
            {"RIGHT_ID": "product", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["AMINO_ACID", "ORGANISM_SUBSTANCE", "SIMPLE_CHEMICAL"]}}, "LEFT_ID": "verb", "REL_OP": ">"}
        ]
    ],
    "CONTAINS": [
        # Original pattern
        [
            {"RIGHT_ID": "aa", "RIGHT_ATTRS": {"ENT_TYPE": "AMINO_ACID"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": "contain"}, "LEFT_ID": "aa", "REL_OP": ">"},
            {"RIGHT_ID": "chem", "RIGHT_ATTRS": {"ENT_TYPE": "SIMPLE_CHEMICAL"}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Enhanced with more container-content relationships
        [
            {"RIGHT_ID": "container", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CELLULAR_COMPONENT", "ORGAN", "TISSUE", "CELL"]}}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["contain", "include", "comprise", "harbor"]}}, "LEFT_ID": "container", "REL_OP": ">"},
            {"RIGHT_ID": "content", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["GENE_OR_GENE_PRODUCT", "SIMPLE_CHEMICAL", "AMINO_ACID"]}}, "LEFT_ID": "verb", "REL_OP": ">"}
        ]
    ],
    "BINDS": [
        # Original pattern
        [
            {"RIGHT_ID": "protein", "RIGHT_ATTRS": {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": "bind"}, "LEFT_ID": "protein", "REL_OP": ">"},
            {"RIGHT_ID": "chem", "RIGHT_ATTRS": {"ENT_TYPE": "SIMPLE_CHEMICAL"}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Enhanced with interaction verbs
        [
            {"RIGHT_ID": "protein", "RIGHT_ATTRS": {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["interact", "associate", "complex"]}}, "LEFT_ID": "protein", "REL_OP": ">"},
            {"RIGHT_ID": "target", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["SIMPLE_CHEMICAL", "GENE_OR_GENE_PRODUCT"]}}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Bidirectional binding
        [
            {"RIGHT_ID": "chem", "RIGHT_ATTRS": {"ENT_TYPE": "SIMPLE_CHEMICAL"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["bind", "interact"]}}, "LEFT_ID": "chem", "REL_OP": ">"},
            {"RIGHT_ID": "protein", "RIGHT_ATTRS": {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, "LEFT_ID": "verb", "REL_OP": ">"}
        ]
    ],
    "REGULATES": [
        # Original pattern
        [
            {"RIGHT_ID": "regulator", "RIGHT_ATTRS": {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": "regulate"}, "LEFT_ID": "regulator", "REL_OP": ">"},
            {"RIGHT_ID": "target", "RIGHT_ATTRS": {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Enhanced with regulatory terms
        [
            {"RIGHT_ID": "regulator", "RIGHT_ATTRS": {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["control", "modulate", "influence", "upregulate", "downregulate", "activate", "inhibit"]}}, "LEFT_ID": "regulator", "REL_OP": ">"},
            {"RIGHT_ID": "target", "RIGHT_ATTRS": {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, "LEFT_ID": "verb", "REL_OP": ">"}
        ]
    ],
    "EXPRESSED_IN": [
        # Original pattern
        [
            {"RIGHT_ID": "gene", "RIGHT_ATTRS": {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": "express"}, "LEFT_ID": "gene", "REL_OP": ">"},
            {"RIGHT_ID": "cell", "RIGHT_ATTRS": {"ENT_TYPE": "CELL"}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Enhanced with expression and location terms
        [
            {"RIGHT_ID": "gene", "RIGHT_ATTRS": {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["express", "present", "detect", "find", "localize"]}}, "LEFT_ID": "gene", "REL_OP": ">"},
            {"RIGHT_ID": "location", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CELL", "TISSUE", "ORGAN", "CANCER"]}}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Overexpression pattern
        [
            {"RIGHT_ID": "gene", "RIGHT_ATTRS": {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}},
            {"RIGHT_ID": "adj", "RIGHT_ATTRS": {"LOWER": {"IN": ["overexpressed", "upregulated", "elevated"]}}, "LEFT_ID": "gene", "REL_OP": ">"},
            {"RIGHT_ID": "location", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CELL", "TISSUE", "CANCER"]}}, "LEFT_ID": "adj", "REL_OP": ">"}
        ]
    ],
    "MUTATED_IN": [
        # Original pattern
        [
            {"RIGHT_ID": "gene", "RIGHT_ATTRS": {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}},
            {"RIGHT_ID": "mutation", "RIGHT_ATTRS": {"LEMMA": "mutation"}, "LEFT_ID": "gene", "REL_OP": ">"},
            {"RIGHT_ID": "cancer", "RIGHT_ATTRS": {"ENT_TYPE": "CANCER"}, "LEFT_ID": "mutation", "REL_OP": ">"}
        ],
        # Enhanced with mutation types
        [
            {"RIGHT_ID": "gene", "RIGHT_ATTRS": {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["mutate", "alter", "delete", "amplify"]}}, "LEFT_ID": "gene", "REL_OP": ">"},
            {"RIGHT_ID": "cancer", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CANCER", "CELL"]}}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Loss/inactivation pattern
        [
            {"RIGHT_ID": "gene", "RIGHT_ATTRS": {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}},
            {"RIGHT_ID": "noun", "RIGHT_ATTRS": {"LEMMA": {"IN": ["loss", "inactivation", "deletion"]}}, "LEFT_ID": "gene", "REL_OP": ">"},
            {"RIGHT_ID": "cancer", "RIGHT_ATTRS": {"ENT_TYPE": "CANCER"}, "LEFT_ID": "noun", "REL_OP": ">"}
        ]
    ],
    "PART_OF": [
        # Original pattern
        [
            {"RIGHT_ID": "part", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CELL", "CELLULAR_COMPONENT", "TISSUE", "ORGAN"]}}},
            {"RIGHT_ID": "prep", "RIGHT_ATTRS": {"LEMMA": "part"}, "LEFT_ID": "part", "REL_OP": ">"},
            {"RIGHT_ID": "whole", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["TISSUE", "ORGAN", "MULTI_TISSUE_STRUCTURE", "ANATOMICAL_SYSTEM", "ORGANISM"]}}, "LEFT_ID": "prep", "REL_OP": ">"}
        ],
        # Enhanced structural relationships
        [
            {"RIGHT_ID": "component", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CELLULAR_COMPONENT", "CELL", "TISSUE"]}}},
            {"RIGHT_ID": "noun", "RIGHT_ATTRS": {"LEMMA": {"IN": ["component", "element", "constituent"]}}, "LEFT_ID": "component", "REL_OP": ">"},
            {"RIGHT_ID": "whole", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CELL", "TISSUE", "ORGAN", "MULTI_TISSUE_STRUCTURE"]}}, "LEFT_ID": "noun", "REL_OP": ">"}
        ]
    ],
    "LOCATED_IN": [
        # Original pattern
        [
            {"RIGHT_ID": "entity", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CELL", "ORGAN"]}}},
            {"RIGHT_ID": "loc", "RIGHT_ATTRS": {"LEMMA": "locate"}, "LEFT_ID": "entity", "REL_OP": ">"},
            {"RIGHT_ID": "place", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["ORGAN", "ORGANISM_SUBDIVISION", "MULTI_TISSUE_STRUCTURE"]}}, "LEFT_ID": "loc", "REL_OP": ">"}
        ],
        # Enhanced location patterns
        [
            {"RIGHT_ID": "entity", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["GENE_OR_GENE_PRODUCT", "CELLULAR_COMPONENT", "CELL"]}}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["find", "present", "situate", "localize"]}}, "LEFT_ID": "entity", "REL_OP": ">"},
            {"RIGHT_ID": "place", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CELL", "CELLULAR_COMPONENT", "TISSUE", "ORGAN"]}}, "LEFT_ID": "verb", "REL_OP": ">"}
        ]
    ],
    "ORIGIN_OF": [
        # Original pattern
        [
            {"RIGHT_ID": "cell", "RIGHT_ATTRS": {"ENT_TYPE": "CELL"}},
            {"RIGHT_ID": "origin", "RIGHT_ATTRS": {"LEMMA": "origin"}, "LEFT_ID": "cell", "REL_OP": ">"},
            {"RIGHT_ID": "cancer", "RIGHT_ATTRS": {"ENT_TYPE": "CANCER"}, "LEFT_ID": "origin", "REL_OP": ">"}
        ],
        # Enhanced origin patterns
        [
            {"RIGHT_ID": "source", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CELL", "TISSUE"]}}},
            {"RIGHT_ID": "noun", "RIGHT_ATTRS": {"LEMMA": {"IN": ["source", "precursor", "origin"]}}, "LEFT_ID": "source", "REL_OP": ">"},
            {"RIGHT_ID": "cancer", "RIGHT_ATTRS": {"ENT_TYPE": "CANCER"}, "LEFT_ID": "noun", "REL_OP": ">"}
        ]
    ],
    "CONTAINS_COMPONENT": [
        # Original pattern
        [
            {"RIGHT_ID": "component", "RIGHT_ATTRS": {"ENT_TYPE": "CELLULAR_COMPONENT"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": "contain"}, "LEFT_ID": "component", "REL_OP": ">"},
            {"RIGHT_ID": "gene", "RIGHT_ATTRS": {"ENT_TYPE": "GENE_OR_GENE_PRODUCT"}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Enhanced component patterns
        [
            {"RIGHT_ID": "container", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CELLULAR_COMPONENT", "CELL", "ORGAN"]}}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["contain", "include", "comprise", "house"]}}, "LEFT_ID": "container", "REL_OP": ">"},
            {"RIGHT_ID": "content", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["GENE_OR_GENE_PRODUCT", "SIMPLE_CHEMICAL", "AMINO_ACID"]}}, "LEFT_ID": "verb", "REL_OP": ">"}
        ]
    ],
    "SURROUNDS": [
        # Original pattern
        [
            {"RIGHT_ID": "immaterial", "RIGHT_ATTRS": {"ENT_TYPE": "IMMATERIAL_ANATOMICAL_ENTITY"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": "surround"}, "LEFT_ID": "immaterial", "REL_OP": ">"},
            {"RIGHT_ID": "organ", "RIGHT_ATTRS": {"ENT_TYPE": "ORGAN"}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Enhanced surrounding patterns
        [
            {"RIGHT_ID": "surrounder", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["TISSUE", "CELLULAR_COMPONENT", "IMMATERIAL_ANATOMICAL_ENTITY"]}}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["surround", "encircle", "enclose"]}}, "LEFT_ID": "surrounder", "REL_OP": ">"},
            {"RIGHT_ID": "surrounded", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["ORGAN", "CELL", "TISSUE"]}}, "LEFT_ID": "verb", "REL_OP": ">"}
        ]
    ],
    "DEVELOPS_INTO": [
        # Original pattern
        [
            {"RIGHT_ID": "dev", "RIGHT_ATTRS": {"ENT_TYPE": "DEVELOPING_ANATOMICAL_STRUCTURE"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": "develop"}, "LEFT_ID": "dev", "REL_OP": ">"},
            {"RIGHT_ID": "organ", "RIGHT_ATTRS": {"ENT_TYPE": "ORGAN"}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Enhanced development patterns
        [
            {"RIGHT_ID": "precursor", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["DEVELOPING_ANATOMICAL_STRUCTURE", "CELL"]}}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["differentiate", "mature", "transform", "become"]}}, "LEFT_ID": "precursor", "REL_OP": ">"},
            {"RIGHT_ID": "mature", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["ORGAN", "TISSUE", "CELL"]}}, "LEFT_ID": "verb", "REL_OP": ">"}
        ]
    ],
    "ORIGINATES_FROM": [
        # Original pattern
        [
            {"RIGHT_ID": "cancer", "RIGHT_ATTRS": {"ENT_TYPE": "CANCER"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": "originate"}, "LEFT_ID": "cancer", "REL_OP": ">"},
            {"RIGHT_ID": "organ", "RIGHT_ATTRS": {"ENT_TYPE": "ORGAN"}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Enhanced origin patterns
        [
            {"RIGHT_ID": "cancer", "RIGHT_ATTRS": {"ENT_TYPE": "CANCER"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["derive", "stem", "originate"]}}, "LEFT_ID": "cancer", "REL_OP": ">"},
            {"RIGHT_ID": "source", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["ORGAN", "TISSUE", "CELL"]}}, "LEFT_ID": "verb", "REL_OP": ">"}
        ]
    ],
    "ARISES_FROM": [
        # Original pattern
        [
            {"RIGHT_ID": "cancer", "RIGHT_ATTRS": {"ENT_TYPE": "CANCER"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": "arise"}, "LEFT_ID": "cancer", "REL_OP": ">"},
            {"RIGHT_ID": "cell", "RIGHT_ATTRS": {"ENT_TYPE": "CELL"}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Enhanced arising patterns
        [
            {"RIGHT_ID": "pathology", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CANCER", "PATHOLOGICAL_FORMATION"]}}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["arise", "emerge", "develop"]}}, "LEFT_ID": "pathology", "REL_OP": ">"},
            {"RIGHT_ID": "source", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CELL", "TISSUE"]}}, "LEFT_ID": "verb", "REL_OP": ">"}
        ]
    ],
    "AFFECTS": [
        # Original pattern
        [
            {"RIGHT_ID": "path", "RIGHT_ATTRS": {"ENT_TYPE": "PATHOLOGICAL_FORMATION"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": "affect"}, "LEFT_ID": "path", "REL_OP": ">"},
            {"RIGHT_ID": "organ", "RIGHT_ATTRS": {"ENT_TYPE": "ORGAN"}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Enhanced effect patterns
        [
            {"RIGHT_ID": "agent", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["PATHOLOGICAL_FORMATION", "CANCER", "SIMPLE_CHEMICAL"]}}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["affect", "impact", "influence", "involve", "target"]}}, "LEFT_ID": "agent", "REL_OP": ">"},
            {"RIGHT_ID": "target", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["ORGAN", "TISSUE", "CELL"]}}, "LEFT_ID": "verb", "REL_OP": ">"}
        ]
    ],
    "ASSOCIATED_WITH": [
        # Original pattern
        [
            {"RIGHT_ID": "path", "RIGHT_ATTRS": {"ENT_TYPE": "PATHOLOGICAL_FORMATION"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": "associate"}, "LEFT_ID": "path", "REL_OP": ">"},
            {"RIGHT_ID": "cancer", "RIGHT_ATTRS": {"ENT_TYPE": "CANCER"}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Enhanced association patterns
        [
            {"RIGHT_ID": "entity1", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["GENE_OR_GENE_PRODUCT", "SIMPLE_CHEMICAL", "PATHOLOGICAL_FORMATION"]}}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["associate", "correlate", "link", "relate"]}}, "LEFT_ID": "entity1", "REL_OP": ">"},
            {"RIGHT_ID": "entity2", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CANCER", "PATHOLOGICAL_FORMATION"]}}, "LEFT_ID": "verb", "REL_OP": ">"}
        ]
    ],
    "DAMAGES": [
        # Original pattern
        [
            {"RIGHT_ID": "path", "RIGHT_ATTRS": {"ENT_TYPE": "PATHOLOGICAL_FORMATION"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": "damage"}, "LEFT_ID": "path", "REL_OP": ">"},
            {"RIGHT_ID": "tissue", "RIGHT_ATTRS": {"ENT_TYPE": "TISSUE"}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Enhanced damage patterns
        [
            {"RIGHT_ID": "agent", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["PATHOLOGICAL_FORMATION", "SIMPLE_CHEMICAL", "CANCER"]}}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["damage", "harm", "injure", "destroy", "invade"]}}, "LEFT_ID": "agent", "REL_OP": ">"},
            {"RIGHT_ID": "target", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["TISSUE", "ORGAN", "CELL"]}}, "LEFT_ID": "verb", "REL_OP": ">"}
        ]
    ],
    "BIOMARKER_FOR": [
        # Original pattern
        [
            {"RIGHT_ID": "substance", "RIGHT_ATTRS": {"ENT_TYPE": "ORGANISM_SUBSTANCE"}},
            {"RIGHT_ID": "noun", "RIGHT_ATTRS": {"LEMMA": "biomarker"}, "LEFT_ID": "substance", "REL_OP": ">"},
            {"RIGHT_ID": "cancer", "RIGHT_ATTRS": {"ENT_TYPE": "CANCER"}, "LEFT_ID": "noun", "REL_OP": ">"}
        ],
        # Enhanced biomarker patterns
        [
            {"RIGHT_ID": "marker", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["GENE_OR_GENE_PRODUCT", "ORGANISM_SUBSTANCE", "SIMPLE_CHEMICAL"]}}},
            {"RIGHT_ID": "noun", "RIGHT_ATTRS": {"LEMMA": {"IN": ["biomarker", "marker", "indicator"]}}, "LEFT_ID": "marker", "REL_OP": ">"},
            {"RIGHT_ID": "disease", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CANCER", "PATHOLOGICAL_FORMATION"]}}, "LEFT_ID": "noun", "REL_OP": ">"}
        ],
        # Elevated/overexpressed pattern
        [
            {"RIGHT_ID": "marker", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["GENE_OR_GENE_PRODUCT", "ORGANISM_SUBSTANCE"]}}},
            {"RIGHT_ID": "adj", "RIGHT_ATTRS": {"LEMMA": {"IN": ["elevated", "overexpressed", "increased"]}}, "LEFT_ID": "marker", "REL_OP": ">"},
            {"RIGHT_ID": "disease", "RIGHT_ATTRS": {"ENT_TYPE": "CANCER"}, "LEFT_ID": "adj", "REL_OP": ">"}
        ]
    ],
    "TOXIC_TO": [
        # Original pattern
        [
            {"RIGHT_ID": "chem", "RIGHT_ATTRS": {"ENT_TYPE": "SIMPLE_CHEMICAL"}},
            {"RIGHT_ID": "adj", "RIGHT_ATTRS": {"LEMMA": "toxic"}, "LEFT_ID": "chem", "REL_OP": ">"},
            {"RIGHT_ID": "cell", "RIGHT_ATTRS": {"ENT_TYPE": "CELL"}, "LEFT_ID": "adj", "REL_OP": ">"}
        ],
        # Enhanced toxicity patterns
        [
            {"RIGHT_ID": "chem", "RIGHT_ATTRS": {"ENT_TYPE": "SIMPLE_CHEMICAL"}},
            {"RIGHT_ID": "adj", "RIGHT_ATTRS": {"LEMMA": {"IN": ["toxic", "harmful", "cytotoxic", "poisonous"]}}, "LEFT_ID": "chem", "REL_OP": ">"},
            {"RIGHT_ID": "target", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CELL", "TISSUE", "ORGAN"]}}, "LEFT_ID": "adj", "REL_OP": ">"}
        ],
        # Killing pattern
        [
            {"RIGHT_ID": "chem", "RIGHT_ATTRS": {"ENT_TYPE": "SIMPLE_CHEMICAL"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["kill", "destroy"]}}, "LEFT_ID": "chem", "REL_OP": ">"},
            {"RIGHT_ID": "target", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CELL", "CANCER"]}}, "LEFT_ID": "verb", "REL_OP": ">"}
        ]
    ],
    "COMPONENT_OF": [
        # Original pattern
        [
            {"RIGHT_ID": "chem", "RIGHT_ATTRS": {"ENT_TYPE": "SIMPLE_CHEMICAL"}},
            {"RIGHT_ID": "noun", "RIGHT_ATTRS": {"LEMMA": "component"}, "LEFT_ID": "chem", "REL_OP": ">"},
            {"RIGHT_ID": "substance", "RIGHT_ATTRS": {"ENT_TYPE": "ORGANISM_SUBSTANCE"}, "LEFT_ID": "noun", "REL_OP": ">"}
        ],
        # Enhanced component patterns
        [
            {"RIGHT_ID": "part", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["SIMPLE_CHEMICAL", "AMINO_ACID", "GENE_OR_GENE_PRODUCT"]}}},
            {"RIGHT_ID": "noun", "RIGHT_ATTRS": {"LEMMA": {"IN": ["component", "constituent", "element", "part"]}}, "LEFT_ID": "part", "REL_OP": ">"},
            {"RIGHT_ID": "whole", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["ORGANISM_SUBSTANCE", "CELLULAR_COMPONENT", "CELL"]}}, "LEFT_ID": "noun", "REL_OP": ">"}
        ]
    ],
    "SECRETED_BY": [
        # Original pattern
        [
            {"RIGHT_ID": "substance", "RIGHT_ATTRS": {"ENT_TYPE": "ORGANISM_SUBSTANCE"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": "secrete"}, "LEFT_ID": "substance", "REL_OP": ">"},
            {"RIGHT_ID": "organ", "RIGHT_ATTRS": {"ENT_TYPE": "ORGAN"}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Enhanced secretion patterns
        [
            {"RIGHT_ID": "substance", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["ORGANISM_SUBSTANCE", "SIMPLE_CHEMICAL"]}}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["secrete", "release", "produce", "excrete"]}}, "LEFT_ID": "substance", "REL_OP": ">"},
            {"RIGHT_ID": "secretor", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["ORGAN", "CELL", "TISSUE"]}}, "LEFT_ID": "verb", "REL_OP": ">"}
        ]
    ],
    "TREATS": [
        # Original pattern
        [
            {"RIGHT_ID": "chem", "RIGHT_ATTRS": {"ENT_TYPE": "SIMPLE_CHEMICAL"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": "treat"}, "LEFT_ID": "chem", "REL_OP": ">"},
            {"RIGHT_ID": "path", "RIGHT_ATTRS": {"ENT_TYPE": "PATHOLOGICAL_FORMATION"}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Enhanced treatment patterns
        [
            {"RIGHT_ID": "chem", "RIGHT_ATTRS": {"ENT_TYPE": "SIMPLE_CHEMICAL"}},
            {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"LEMMA": {"IN": ["treat", "cure", "heal", "inhibit", "block", "suppress"]}}, "LEFT_ID": "chem", "REL_OP": ">"},
            {"RIGHT_ID": "disease", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["PATHOLOGICAL_FORMATION", "CANCER"]}}, "LEFT_ID": "verb", "REL_OP": ">"}
        ],
        # Drug effectiveness pattern
        [
            {"RIGHT_ID": "chem", "RIGHT_ATTRS": {"ENT_TYPE": "SIMPLE_CHEMICAL"}},
            {"RIGHT_ID": "adj", "RIGHT_ATTRS": {"LEMMA": {"IN": ["effective", "active"]}}, "LEFT_ID": "chem", "REL_OP": ">"},
            {"RIGHT_ID": "disease", "RIGHT_ATTRS": {"ENT_TYPE": {"IN": ["CANCER", "PATHOLOGICAL_FORMATION"]}}, "LEFT_ID": "adj", "REL_OP": ">"}
        ]
    ]
}


GENERIC_ENTITIES = {
    '-resistant cell lines',
    '-resistant cells',
    'resistant cell lines',
    'resistant cells',
    'adult cancer patients',
    'adult patients',
    'adult tissues',
    'advanced cancer patients',
    'advanced-stage cancer',
    'advanced-stage disease',
    'advanced-stage tumors',
    'advanced/metastatic solid tumors',
    'benign cells',
    'benign disease',
    'benign epithelial tissues',
    'benign lesions.',
    'benign neoplasm',
    'benign tissues',
    'cancer cancer',
    'cancer cell',
    'cancer cell line',
    'cancer cell lines',
    'cancer female',
    'cancer patient',
    'cancer patients',
    'cancer tissue',
    'cancer tissues',
    'cancers',
    'carcinoma',
    'carcinoma cancer',
    'carcinoma cells',
    'carcinoma disease',
    'carcinoma epithelial cells',
    'carcinoma tissue',
    'cell',
    'cell cancer',
    'cell carcinoma',
    'cell carcinoma tissues',
    'cell line',
    'cell malignancy',
    'cell-to-cell',
    'celllines',
    'cells cell',
    'cells cell line',
    'control-patients',
    'disease',
    'disease cancer',
    'early lesions',
    'early-stage cancers',
    'early-stage disease',
    'early-stage patients',
    'early-stage tumors',
    'epithelial cancer',
    'epithelial cancers',
    'epithelial cell line',
    'epithelial cells',
    'epithelial cells cell',
    'epithelial malignancy',
    'epithelial tumor tissues',
    'epithelial tumors',
    'high cell',
    'high-grade advanced stage tumors',
    'high-grade cancer',
    'high-grade disease',
    'high-grade invasive cancer',
    'high-grade tumor',
    'high-grade tumours',
    'human cancer',
    'human cancer cell lines',
    'human cancer tissues',
    'human cancers',
    'human disease',
    'human epithelial cancers',
    'human epithelial malignancies',
    'human malignancies',
    'human malignant cell lines',
    'human malignant neoplasms: a',
    'human malignant tumors',
    'human organs',
    'human patients',
    'human solid cancers',
    'human solid tumors',
    'human tissues',
    'human tumor cell lines',
    'human tumor cells',
    'human tumor patients',
    'human tumor tissue',
    'human tumor tissues',
    'human tumors',
    'human tumour',
    'large-cell',
    'late-line',
    'lesions',
    'line',
    'lines',
    'low cancer',
    'low-grade cancer',
    'low-grade disease',
    'low-grade patients',
    'low-grade tumors',
    'low-grade tumours',
    'male female cell',
    'male female cell line',
    'malignancy cancer',
    'malignancy disease',
    'malignancy tumors',
    'malignant cancer',
    'malignant cancer cell',
    'malignant carcinoma',
    'malignant conditions',
    'malignant disease',
    'malignant diseases',
    'malignant epithelial cell',
    'malignant epithelial cells',
    'malignant lesions',
    'malignant tissue',
    'malignant tissues',
    'malignant tumor cell',
    'malignant tumor tissues',
    'metastatic cancer patients',
    'metastatic cancers patients',
    'metastatic cells',
    'metastatic disease organ',
    'metastatic lesions',
    'metastatic solid tumors',
    'metastatic tumor cell',
    'metastatic tumors',
    'mice animals cell line',
    'mice cancer cell',
    'mice carcinoma',
    'mice cell',
    'mice cell line',
    'mice male cell line',
    'mice neoplasm',
    'mice neoplasms cell line',
    'mouse cancer cells',
    'mouse tissue',
    'mouse tissues',
    'mouse tumor',
    'mouse tumors',
    'mouse tumour',
    'murine cancer',
    'murine organs',
    'murine tumor',
    'neoplasm animals cell line',
    'neoplasm carcinoma cell line',
    'neoplasm cell',
    'neoplasm cell line',
    'neoplasm disease',
    'neoplasm epithelial',
    'neoplasm female',
    'neoplasm female male',
    'neoplasm female tumor',
    'neoplasm male',
    'neoplasm male mice',
    'neoplasm mice',
    'neoplasm mice female',
    'neoplasm mice mice',
    'neoplasms cell',
    'neoplasms cell line',
    'neoplasms disease',
    'neoplasms male female',
    'neoplasms mice',
    'neoplasms mice male',
    'neoplasms organ',
    'neoplasms patient',
    'neoplasms tissue',
    'non-advanced tumour',
    'non-cancer',
    'non-cancer patients',
    'non-carcinoma tissues',
    'non-epithelial cells',
    'non-human tissues',
    'non-malignant cell',
    'non-malignant tissues',
    'non-metastatic patients',
    'non-organ',
    'non-small cell',
    'non-small cell carcinoma',
    'non-tumor',
    'non-tumor cell',
    'non-tumor cell line',
    'non-tumor cells',
    'non-tumor tissues',
    'non-tumour tissues',
    'organ',
    'organ malignancies',
    'organ tissue',
    'organ tissues',
    'organs/tissues',
    'pathology',
    'patient',
    'patient tissue',
    'patient tissues',
    'patient tumor tissues',
    'patient tumors',
    'patients',
    'patients patient',
    'primary lesions',
    'primary malignant tumors',
    'primary tumors',
    'resectable cancer',
    'resectable cancers',
    'resectable lesions',
    'resectable tumors',
    'resectable tumours',
    'resistant-cell',
    'small-cell',
    'small-cell tumors',
    'solid cancer tissue',
    'solid cancers',
    'solid carcinomas',
    'solid malignancies',
    'solid malignancy',
    'solid malignant tumors',
    'solid organ cancer',
    'solid organ cancers',
    'solid organ malignancies',
    'solid organ tumors',
    'solid organ tumours',
    'solid tissue',
    'solid tumor cancer',
    'solid tumor tissues',
    'solid tumors',
    'solid-organ',
    'stage epithelial solid tumors',
    'subjects',
    'tissue',
    'tissue cells',
    'tissues/cells',
    'tumor',
    'tumor animals cell',
    'tumor animals cell line',
    'tumor animals tumor',
    'tumor cancer',
    'tumor cancer cell',
    'tumor cancer cells cell',
    'tumor cancer mice',
    'tumor carcinoma cell',
    'tumor cell',
    'tumor cell line',
    'tumor disease',
    'tumor epithelial',
    'tumor epithelial cell',
    'tumor female cell',
    'tumor female tissue',
    'tumor female tumor',
    'tumor grade',
    'tumor human cancers',
    'tumor lesions',
    'tumor male',
    'tumor male female',
    'tumor male female cell',
    'tumor malignancies',
    'tumor malignancy',
    'tumor mice',
    'tumor mice carcinoma',
    'tumor mice cell',
    'tumor mice cell line',
    'tumor mice neoplasm',
    'tumor mice neoplasms',
    'tumor neoplasm',
    'tumor neoplasms',
    'tumor patient',
    'tumor patients',
    'tumor tissue',
    'tumor tissue human',
    'tumor tumor',
    'tumor tumours',
    'tumor-to-tumor',
    'tumour cells',
    'tumour lesions',
    'tumour tissues',
    'unresectable cancer',
    'unresectable solid tumors',
    'unresectable tumours'
}




if __name__ == "__main__":
    #to make sure we have the same relations in both
    are_similar = MATCHER_PATTERNS.keys() == DEPENDENCY_MATCHER_PATTERNS.keys()
    if are_similar:
        print("we have the same relations types for matchers and dependency matchers.")
        print("relations types: ", MATCHER_PATTERNS.keys())
    else:
        print("warning: we don't the same relations types for matchers and dependency matchers.")
        print("matchers relations types", MATCHER_PATTERNS.keys())
        print("dependency matchers relations types", DEPENDENCY_MATCHER_PATTERNS.keys())


    