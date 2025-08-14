import pandas as pd 

import uuid
import logging

def prepare_data_for_neo4j(raw_ents_path, raw_rels_path, saving_dir):
	"""Parameters: 
	raw_ents_path = path to the raw extracted entities csv
	raw_rels_path = path to raw extracted relations csv
	saving_dir = path of the directory to which cleaned data will be saved"""
	entities = pd.read_csv(raw_ents_path)
	relations = pd.read_csv(raw_rels_path)

	if 'Unnamed: 0' in entities.columns: entities.drop(columns=['Unnamed: 0'], inplace=True)
	if 'Unnamed: 0' in relations.columns: relations.drop(columns=['Unnamed: 0'], inplace=True)


	#entities cleaning
	print("entities records before:", entities.shape[0])
	logging(f"Entities: Before Cleaning: {len(entities)}")
	#separate rows without CUI, because we will be deduplicating using CUI column as subset,
	#  which will cause to lose them as pandas will consider them duplicates.
	rows_with_cui_missing = entities[entities['cui'].isna()]
	rows_with_cui = entities.dropna(subset=['cui'], ignore_index=True)

	#drop CUI duplicates, this is for cases like: cancer cancers etc...
	unique_cui_rows = rows_with_cui.drop_duplicates(subset=['cui'], ignore_index=True)
	logging.info("Entities: Drop CUI duplicates.")
	#combine back unique CUI rows with all missing CUI rows
	entities = pd.concat([unique_cui_rows, rows_with_cui_missing], ignore_index=True)

	#drop duplicates by text & label
	entities['text'] = entities['text'].str.lower()
	entities.drop_duplicates(subset=['text', 'label'], inplace=True, ignore_index=True)
	logging.info("Entities: Drop ['text', 'label'] Duplicates.")
	print("entities records after:", entities.shape[0])
	logging(f"Entities: After Cleaning: {len(entities)}")
	#relations cleaning
	print("relations records before:", relations.shape[0])
	logging(f"Relations: Before Cleaning: {len(relations)}")
	#drop duplicates by ent1 & ent2, I assume here that two entities can only have one relation per direction
	relations['ent1'] = relations['ent1'].str.lower()
	relations['ent2'] = relations['ent2'].str.lower()
	relations.drop_duplicates(subset=['ent1', 'ent2'], inplace=True, ignore_index=True)
	logging.info("Relations: Drop ['ent1', 'ent2'] Duplicates.")
	print("relations records after:", relations.shape[0])
	logging(f"Relations: After Cleaning: {len(relations)}")


	#renaming columns for Neo4j
	entities.columns = ['name', ':LABEL', 'pmid', 'pmcid', 'fetching_date', 'cui', 'normalized_name', 'normalization_source', 'url']
	#adding an id column 
	entities.insert(
		loc = 0, 
		column= ":ID",
		value= [str(uuid.uuid4()) for _ in range(len(entities))]
		)
	logging.info("Entities: Rename Columns & Add UUID.")
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
	logging.info("Relations: Map To Entities & Rename Columns.")
	#now keep only relation related columns.
	relations = relations[[":START_ID", ":END_ID", ":TYPE", "pmid", "pmcid", "fetching_date"]]

	#export again:
	try: 
		entities.to_csv(f"{saving_dir}/entities4neo4j.csv", index=False)
		relations.to_csv(f"{saving_dir}/relations4neo4j.csv", index = False)
		logging.info(f"Cleaning & Preparation Process Completed. Repo: {saving_dir}.")
	except Exception as e: 
		logging.error(f"Cleaning & Preparation Process Failed: {e}")