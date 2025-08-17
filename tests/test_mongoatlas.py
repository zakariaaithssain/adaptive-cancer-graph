import pytest
from unittest.mock import patch, MagicMock
from pymongo import errors
from modules.mongoatlas import MongoAtlasConnector
from unittest.mock import ANY

# ------------------------
# Fixtures
# ------------------------

@pytest.fixture
def mock_client():
    with patch("modules.mongoatlas.MongoClient") as mock_client_cls:
        mock_cluster = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        # chain __getitem__ to return db and collection
        mock_client_cls.return_value = mock_cluster
        mock_cluster.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        # mock ping to succeed
        mock_cluster.admin.command.return_value = {"ok": 1}

        yield mock_client_cls, mock_cluster, mock_db, mock_collection

# ------------------------
# Test Initialization
# ------------------------

def test_initialization_success(mock_client):
    mock_client_cls, mock_cluster, mock_db, mock_collection = mock_client

    connector = MongoAtlasConnector("fake_connection_str")
    
    mock_client_cls.assert_called_once_with(
        host="fake_connection_str",
        server_api= ANY # just check the parameter exists
    )
    mock_cluster.admin.command.assert_called_once_with("ping")
    mock_collection.create_index.assert_called_once_with("pmid", unique=True)
    assert connector.db == mock_db
    assert connector.collection == mock_collection

def test_initialization_failure():
    with patch("modules.mongoatlas.MongoClient") as mock_client_cls:
        mock_cluster = MagicMock()
        mock_cluster.admin.command.side_effect = Exception("Ping Failed")
        mock_client_cls.return_value = mock_cluster
        
        with pytest.raises(Exception, match="Ping Failed"):
            MongoAtlasConnector("fake_connection_str")

# ------------------------
# Test load_articles_to_atlas
# ------------------------

def test_load_articles_inserts_only_non_empty(mock_client):
    _, _, _, mock_collection = mock_client

    connector = MongoAtlasConnector("fake_connection_str")
    articles = [
        {"pmid": "1", "abstract": "Some abstract"},
        {"pmid": "2", "abstract": ""},  # should be ignored
        {"pmid": "3", "abstract": None}, # should be ignored
    ]
    connector.load_articles_to_atlas(articles)

    # Only first article should be inserted
    mock_collection.update_one.assert_called_once()
    args, kwargs = mock_collection.update_one.call_args
    assert args[0] == {"pmid": "1"}
    assert "$setOnInsert" in args[1]

def test_load_articles_handles_pymongo_error(mock_client):
    _, _, _, mock_collection = mock_client
    mock_collection.update_one.side_effect = errors.PyMongoError("Fail")

    connector = MongoAtlasConnector("fake_connection_str")
    articles = [{"pmid": "1", "abstract": "Some abstract"}]
    
    # Should not raise, just log error
    connector.load_articles_to_atlas(articles)

# ------------------------
# Test fetch_articles_from_atlas
# ------------------------

def test_fetch_articles_returns_filtered_docs(mock_client):
    _, _, _, mock_collection = mock_client
    # return cursor with mocked documents
    mock_cursor = [
        {
            "pmid": "1",
            "title": "Title1",
            "abstract": "Abstract1",
            "keywords": ["k1"],
            "medical_subject_headings": ["m1"],
            "fetchingdate": "2025-01-01T00:00:00Z"
        },
        {
            "pmid": "2",
            "title": "Title2",
            "abstract": None,  # will be ignored
            "keywords": [],
            "medical_subject_headings": [],
            "fetchingdate": "2025-01-01T00:00:00Z"
        }
    ]
    mock_collection.find.return_value = mock_cursor

    connector = MongoAtlasConnector("fake_connection_str")
    articles = connector.fetch_articles_from_atlas()

    assert len(articles) == 1
    assert articles[0]["pmid"] == "1"
    assert "Abstract1" in articles[0]["text"]
    assert "Title1" in articles[0]["text"]
    assert "k1" in articles[0]["text"]
    assert "m1" in articles[0]["text"]

def test_fetch_articles_handles_pymongo_error(mock_client):
    _, _, _, mock_collection = mock_client
    mock_collection.find.side_effect = errors.PyMongoError("Fail")
    
    connector = MongoAtlasConnector("fake_connection_str")
    
    with pytest.raises(errors.PyMongoError, match="Fail"):
        connector.fetch_articles_from_atlas()

# ------------------------
# Parametrized test for abstract_only behavior
# ------------------------

@pytest.mark.parametrize(
    "abstract,expected_calls",
    [("Some abstract", 1), ("", 0), (None, 0)]
)
def test_load_articles_parametrized(mock_client, abstract, expected_calls):
    _, _, _, mock_collection = mock_client

    connector = MongoAtlasConnector("fake_connection_str")
    articles = [{"pmid": "1", "abstract": abstract}]
    connector.load_articles_to_atlas(articles)

    assert mock_collection.update_one.call_count == expected_calls
