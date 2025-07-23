import pandas as pd
from config.config import PATHS

# Define the relation data
data = [
    ("Gene", "HAS_MUTATION", "Mutation", "BRCA1 → HAS_MUTATION → BRCA1 c.68_69delAG"),
    ("Mutation", "ASSOCIATED_WITH", "Tumor", "BRAF V600E → ASSOCIATED_WITH → Melanoma"),
    ("Gene", "ASSOCIATED_WITH", "Tumor", "TP53 → ASSOCIATED_WITH → Lung cancer"),
    ("Gene", "ENCODES", "Protein", "EGFR → ENCODES → EGFR protein"),
    ("Protein", "ASSOCIATED_WITH", "Tumor", "HER2 → ASSOCIATED_WITH → Breast cancer"),
    ("Protein", "PART_OF", "Pathway", "EGFR → PART_OF → MAPK signaling pathway"),
    ("Pathway", "REGULATES", "Function", "PI3K → REGULATES → Cell growth"),
    ("Gene", "REGULATES", "Function", "TP53 → REGULATES → Apoptosis"),
    ("Protein", "REGULATES", "Function", "Caspase-3 → REGULATES → Apoptosis"),
    ("RiskFactor", "ASSOCIATED_WITH", "Tumor", "Smoking → ASSOCIATED_WITH → Lung cancer"),
    ("RiskFactor", "ASSOCIATED_WITH", "Mutation", "UV → ASSOCIATED_WITH → DNA breaks"),
    ("Treatment", "TREATS", "Tumor", "Chemotherapy → TREATS → Leukemia"),
    ("Treatment", "TARGETS", "Protein", "Trastuzumab → TARGETS → HER2"),
    ("Treatment", "TARGETS", "Mutation", "Osimertinib → TARGETS → EGFR mutation"),
    ("Treatment", "INHIBITS", "Pathway", "Vemurafenib → INHIBITS → MAPK pathway"),
    ("Tumor", "LOCATED_IN", "Organ", "Tumor → LOCATED_IN → Prostate"),
    ("CancerType", "PROPAGATES_TO", "CancerType", "Breast cancer → PROPAGATES_TO → Bone cancer"),
    ("NormalCell", "TRANSFORMS_INTO", "CancerCell", "Luminal cell → TRANSFORMS_INTO → Adenocarcinoma"),
]

# Create DataFrame
df = pd.DataFrame(data, columns=["fromLabel", "relation", "toLabel", "example"])
print(df)

# Save to CSV
csv_path = PATHS["template"]
df.to_csv(csv_path, index=False)
print(f"\nTemplate saved to {csv_path}")
