import pandas as pd
import ast


df = pd.read_json("./data/schema.json")

#transform strings from json to python obj
df["source_nodes"] = df["source_nodes"].apply(lambda x: ast.literal_eval(x))
df["target_nodes"] = df["target_nodes"].apply(lambda x: ast.literal_eval(x))

#exploding the lists where target or source nodes are multiple
df = df.explode("source_nodes", ignore_index=True)
df = df.explode("target_nodes", ignore_index=True)

df.drop(columns=["source_count", "target_count"], inplace=True)
df.drop_duplicates(inplace= True, ignore_index=True)
df.dropna(inplace=True, ignore_index=True)

#check if there remain some None values
print(df[(df.relationship == None) | (df.source_nodes == None) | (df.target_nodes == None)])

df.columns = ["relationship", "fromLabel", "toLabel"]

df.to_csv("./data/template.csv")

print("template saved!")