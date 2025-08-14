import pandas as pd 

import uuid

#TODO: write script to clean the csvs of entities and relations to be ready for Loading step. 
 
entities = pd.read_csv("data/extracted_entities.csv")
relations = pd.read_csv("data/extracted_relations.csv")

if 'Unnamed: 0' in entities.columns: entities.drop(columns=['Unnamed: 0'], inplace=True)
if 'Unnamed: 0' in relations.columns: relations.drop(columns=['Unnamed: 0'], inplace=True)


#entities cleaning
print("entities records before:", entities.shape[0])

#separate rows without CUI, because we will be deduplicating using CUI column as subset,
#  which will cause to lose them as pandas will consider them duplicates.
rows_with_cui_missing = entities[entities['cui'].isna()]
rows_with_cui = entities.dropna(subset=['cui'])

#drop CUI duplicates, this is for cases like: cancer cancers etc...
unique_cui_rows = rows_with_cui.drop_duplicates(subset=['cui'])

#combine back unique CUI rows with all missing CUI rows
entities = pd.concat([unique_cui_rows, rows_with_cui_missing], ignore_index=True)

#drop duplicates by text & label
entities['text'] = entities['text'].str.lower()
entities.drop_duplicates(subset=['text', 'label'], inplace=True)

print("entities records after:", entities.shape[0])

#relations cleaning
print("relations records before:", relations.shape[0])

#drop duplicates by ent1 & ent2, I assume here that two entities can only have one relation per direction
relations['ent1'] = relations['ent1'].str.lower()
relations['ent2'] = relations['ent2'].str.lower()
relations.drop_duplicates(subset=['ent1', 'ent2'], inplace=True)

print("relations records after:", relations.shape[0])


#renaming columns for Neo4j
entities.columns = ['name', ':LABEL', 'pmid', 'pmcid', 'fetching_date', 'cui', 'normalized_name', 'normalization_source', 'url']
#adding an id column 
entities.insert(
    loc = 0, 
    column= ":ID",
    value= [str(uuid.uuid4()) for _ in range(len(entities))]
      )

#mapping relations to names
#select * from relations r join entities e on r.ent1 = a.name 
relations = relations.merge(entities,
                             left_on='ent1', #on which column of the relations
                               right_on= 'name', #on which column of entities
                               )
#select * from relations r join entities e on r.ent2 = a.name 
relations = relations.merge(entities, 
                            left_on= "ent2", 
                            right_on = "name", 
                            #now we will have cui_start cui_end, id_start id_end, etc.. 
                            suffixes= ("_start", "_end") 
                            )

#rename columns for Neo4j
relations = relations.rename(columns={
    ":ID_start": ":START_ID",
    ":ID_end": ":END_ID",
    "relation": ":TYPE"
})

#now keep only relation related columns.
relations = relations[[":START_ID", ":END_ID", ":TYPE", "pmid", "pmcid", "fetching_date"]]

#export again:
entities.to_csv("data/entities4neo4j.csv", index=False)
relations.to_csv("data/relations4neo4j.csv", index = False)