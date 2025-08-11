import pandas as pd

df = pd.read_csv("data/template.csv")

unique = set(df.fromLabel.unique().tolist()).union(set(df.toLabel.unique().tolist()))
print(list(unique))

relations = df.relationship.unique()
print(relations)