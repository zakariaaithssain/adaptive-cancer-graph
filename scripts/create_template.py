import pandas as pd
import ast


df = pd.read_json("./data/schema.json")

#transform strings from json to python obj
df["source_nodes"] = df["source_nodes"].apply(lambda x: ast.literal_eval(x))
df["target_nodes"] = df["target_nodes"].apply(lambda x: ast.literal_eval(x))

#exploding the lists where target or source nodes are multiple
df = df.explode("source_nodes", ignore_index=True)
df = df.explode("target_nodes", ignore_index=True)

#handle missing values
df.drop(columns=["source_count", "target_count"], inplace=True)
df.drop_duplicates(inplace= True, ignore_index=True)
df.dropna(inplace=True, ignore_index=True)

#better names for columns and capitalizing all.
df.columns = ["relationship", "fromLabel", "toLabel"]
df = df.map(lambda x: x.upper() if isinstance(x, str) else x)

df.to_csv("./data/template.csv", index=False)


print("template saved!")