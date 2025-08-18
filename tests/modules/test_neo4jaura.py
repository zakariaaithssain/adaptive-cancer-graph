import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from neo4j.exceptions import Neo4jError
from modules.neo4jaura import Neo4jAuraConnector
from config.neo4jdb_config import NEO4J_LABELS, NEO4J_REL_TYPES

# ---------------- Fixtures ----------------

@pytest.fixture
def mock_driver():
    with patch("modules.neo4jaura.GraphDatabase.driver") as mock_driver_cls:
        mock_driver_instance = MagicMock()
        mock_driver_cls.return_value = mock_driver_instance
        yield mock_driver_instance

@pytest.fixture
def mock_session(mock_driver):
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    yield mock_session

@pytest.fixture
def mock_transaction(mock_session):
    mock_tx = MagicMock()
    mock_session.begin_transaction.return_value.__enter__.return_value = mock_tx
    yield mock_tx

@pytest.fixture
def sample_nodes_csv(tmp_path):
    df = pd.DataFrame({
        ":LABEL": ["GENE_OR_GENE_PRODUCT", "GENE_OR_GENE_PRODUCT"],
        ":ID": ["gene1", "gene2"],
        "name": ["Gene A", "Gene B"],
        "cui": ["C001", "C002"]
    })
    path = tmp_path / "nodes.csv"
    df.to_csv(path, index=False)
    return path

@pytest.fixture
def empty_nodes_csv(tmp_path):
    df = pd.DataFrame(columns=[":LABEL", ":ID", "name", "cui"])
    path = tmp_path / "empty_nodes.csv"
    df.to_csv(path, index=False)
    return path

@pytest.fixture
def sample_rels_csv(tmp_path):
    df = pd.DataFrame({
        ":TYPE": ["AFFECTS", "AFFECTS"],
        "start_id": ["gene1", "gene2"],
        "end_id": ["gene2", "gene1"],
        "pmid": [123, 456]
    })
    path = tmp_path / "rels.csv"
    df.to_csv(path, index=False)
    return path

@pytest.fixture
def empty_rels_csv(tmp_path):
    df = pd.DataFrame(columns=[":TYPE","start_id","end_id","pmid"])
    path = tmp_path / "empty_rels.csv"
    df.to_csv(path, index=False)
    return path

# ---------------- Tests ----------------

# Context manager
def test_context_manager_success(mock_driver):
    connector = Neo4jAuraConnector("fake_uri", auth=("user","pass"))
    with connector as conn:
        assert conn is connector

def test_context_manager_failure(mock_driver):
    mock_driver.session.side_effect = Exception("Conn Fail")
    connector = Neo4jAuraConnector("fake_uri", auth=("user","pass"))
    with pytest.raises(Exception, match="Conn Fail"):
        with connector:
            pass

# ---------------- Entities ----------------
def test_load_ents_success(mock_driver, mock_session, mock_transaction, sample_nodes_csv):
    connector = Neo4jAuraConnector("fake_uri", auth=("user","pass"))
    connector._ents_batch_load = MagicMock()
    connector.load_ents_to_aura(["GENE_OR_GENE_PRODUCT"], str(sample_nodes_csv))
    connector._ents_batch_load.assert_called_once()

def test_load_ents_invalid_label(mock_driver, sample_nodes_csv):
    connector = Neo4jAuraConnector("fake_uri", auth=("user","pass"))
    with pytest.raises(AssertionError):
        connector.load_ents_to_aura(["INVALID"], str(sample_nodes_csv))

def test_get_nodes_with_label_returns_records(mock_driver, sample_nodes_csv):
    connector = Neo4jAuraConnector("fake_uri", auth=("user","pass"))
    nodes = connector._get_nodes_with_label("GENE_OR_GENE_PRODUCT", str(sample_nodes_csv))
    assert len(nodes) == 2
    assert nodes[0]["id"] == "gene1"

def test_get_nodes_with_label_empty(mock_driver, empty_nodes_csv):
    connector = Neo4jAuraConnector("fake_uri", auth=("user","pass"))
    nodes = connector._get_nodes_with_label("GENE_OR_GENE_PRODUCT", str(empty_nodes_csv))
    assert nodes == []

def test_get_nodes_with_label_file_not_found(mock_driver):
    connector = Neo4jAuraConnector("fake_uri", auth=("user","pass"))
    with pytest.raises(FileNotFoundError):
        connector._get_nodes_with_label("GENE_OR_GENE_PRODUCT", "non_existent.csv")

def test_batch_load_ents_raises_neo4j_error(mock_driver, mock_transaction):
    connector = Neo4jAuraConnector("fake_uri", auth=("user","pass"))
    mock_transaction.run.side_effect = Neo4jError("fail")
    with pytest.raises(Neo4jError):
        connector._ents_batch_load("GENE_OR_GENE_PRODUCT", [{"id":"gene1"}], mock_transaction)

def test_batch_load_ents_raises_generic_error(mock_driver, mock_transaction):
    connector = Neo4jAuraConnector("fake_uri", auth=("user","pass"))
    mock_transaction.run.side_effect = Exception("fail")
    with pytest.raises(Exception):
        connector._ents_batch_load("GENE_OR_GENE_PRODUCT", [{"id":"gene1"}], mock_transaction)

# ---------------- Relations ----------------
def test_load_rels_success(mock_driver, mock_session, mock_transaction, sample_rels_csv):
    connector = Neo4jAuraConnector("fake_uri", auth=("user","pass"))
    connector._rels_batch_load = MagicMock()
    connector.load_rels_to_aura(["AFFECTS"], str(sample_rels_csv))
    connector._rels_batch_load.assert_called_once()

def test_load_rels_invalid_type(mock_driver, sample_rels_csv):
    connector = Neo4jAuraConnector("fake_uri", auth=("user","pass"))
    with pytest.raises(AssertionError):
        connector.load_rels_to_aura(["INVALID"], str(sample_rels_csv))

def test_get_relations_with_type_returns_records(mock_driver, sample_rels_csv):
    connector = Neo4jAuraConnector("fake_uri", auth=("user","pass"))
    rels = connector._get_relations_with_type("AFFECTS", str(sample_rels_csv))
    assert len(rels) == 2

def test_get_relations_with_type_empty(mock_driver, empty_rels_csv):
    connector = Neo4jAuraConnector("fake_uri", auth=("user","pass"))
    rels = connector._get_relations_with_type("AFFECTS", str(empty_rels_csv))
    assert rels == []

def test_get_relations_with_type_file_not_found(mock_driver):
    connector = Neo4jAuraConnector("fake_uri", auth=("user","pass"))
    with pytest.raises(FileNotFoundError):
        connector._get_relations_with_type("AFFECTS", "non_existent.csv")

def test_batch_load_rels_raises_neo4j_error(mock_driver, mock_transaction):
    connector = Neo4jAuraConnector("fake_uri", auth=("user","pass"))
    mock_transaction.run.side_effect = Neo4jError("fail")
    with pytest.raises(Neo4jError):
        connector._rels_batch_load("AFFECTS", [{"start_id":"gene1","end_id":"gene2"}], mock_transaction)

def test_batch_load_rels_raises_generic_error(mock_driver, mock_transaction):
    connector = Neo4jAuraConnector("fake_uri", auth=("user","pass"))
    mock_transaction.run.side_effect = Exception("fail")
    with pytest.raises(Exception):
        connector._rels_batch_load("AFFECTS", [{"start_id":"gene1","end_id":"gene2"}], mock_transaction)
