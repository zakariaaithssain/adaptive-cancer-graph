import os
import pandas as pd
import pytest
import tempfile
from scripts.transform.clean import prepare_data_for_neo4j

@pytest.fixture
def tmp_csv_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        ents_path = os.path.join(tmpdir, "entities.csv")
        rels_path = os.path.join(tmpdir, "relations.csv")
        
        # Sample entities, including duplicates and missing CUI
        entities = pd.DataFrame({
            "text": ["Cancer", "Cancer", "Diabetes", "Unknown"],
            "label": ["Disease", "Disease", "Disease", "Disease"],
            "pmid": [1, 1, 2, 3],
            "pmcid": [10, 10, 20, 30],
            "fetching_date": ["2025-01-01"]*4,
            "cui": ["C0001", "C0001", "C0002", None],
            "normalized_name": ["Cancer", "Cancer", "Diabetes", "Unknown"],
            "normalization_source": ["UMLS"]*4,
            "url": [""]*4
        })
        relations = pd.DataFrame({
            "ent1": ["Cancer", "Cancer", "Diabetes"],
            "ent2": ["Diabetes", "Diabetes", "Cancer"],
            "relation": ["related_to", "related_to", "related_to"],
            "pmid": [1, 1, 2],
            "pmcid": [10, 10, 20],
            "fetching_date": ["2025-01-01"]*3
        })

        entities.to_csv(ents_path, index=False)
        relations.to_csv(rels_path, index=False)
        
        yield ents_path, rels_path, tmpdir

def test_prepare_data_creates_files(tmp_csv_files):
    ents_path, rels_path, tmpdir = tmp_csv_files
    out_ents, out_rels = prepare_data_for_neo4j(ents_path, rels_path, tmpdir)
    
    # Files should exist
    assert os.path.exists(out_ents)
    assert os.path.exists(out_rels)
    
    # Entities should have UUID column
    df_ents = pd.read_csv(out_ents)
    assert ":ID" in df_ents.columns
    assert "name" in df_ents.columns
    
    # Relations should have START_ID and END_ID
    df_rels = pd.read_csv(out_rels)
    assert ":START_ID" in df_rels.columns
    assert ":END_ID" in df_rels.columns

def test_deduplication_preserves_missing_cui(tmp_csv_files):
    ents_path, rels_path, tmpdir = tmp_csv_files
    out_ents, _ = prepare_data_for_neo4j(ents_path, rels_path, tmpdir)
    
    df_ents = pd.read_csv(out_ents)
    # Missing CUI row should still exist
    assert df_ents[df_ents['cui'].isna()].shape[0] == 1
    # CUI duplicates should be removed
    assert df_ents[df_ents['cui'] == "C0001"].shape[0] == 1

def test_text_lowercased(tmp_csv_files):
    ents_path, rels_path, tmpdir = tmp_csv_files
    out_ents, _ = prepare_data_for_neo4j(ents_path, rels_path, tmpdir)
    df_ents = pd.read_csv(out_ents)
    
    # Text should be lowercase
    assert all(df_ents['name'] == df_ents['name'].str.lower())


