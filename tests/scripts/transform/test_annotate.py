import pytest
from unittest.mock import MagicMock, patch
import logging

# import the module under test
import scripts.transform.annotate as annotate_module

# ------------------------
# Fixtures
# ------------------------

@pytest.fixture
def mock_connector():
    mock = MagicMock()
    # return fake articles
    mock.fetch_articles_from_atlas.return_value = [
        {"text": "Article 1", "pmid": "1"},
        {"text": "Article 2", "pmid": "2"}
    ]
    return mock

@pytest.fixture
def mock_normalizer():
    return MagicMock()

@pytest.fixture
def mock_nlp():
    mock = MagicMock()
    # chainable methods
    mock.extract_and_normalize_entities.return_value = mock
    mock.extract_relations.return_value = mock
    mock.generate_entities_csv.return_value = mock
    mock.generate_relations_csv.return_value = mock
    return mock

# ------------------------
# Tests
# ------------------------

def test_annotate_mongo_articles_calls_all_steps(mock_connector, mock_normalizer, mock_nlp):
    # patch all dependencies at import time
    with patch("scripts.transform.annotate.MongoAtlasConnector", return_value=mock_connector), \
         patch("scripts.transform.annotate.UMLSNormalizer", return_value=mock_normalizer), \
         patch("scripts.transform.annotate.NLP", return_value=mock_nlp), \
         patch("tqdm.tqdm", lambda x: x):
        
        annotate_module.annotate_mongo_articles(ents_path="fake_extracted_ents.csv", rels_path="fake_extracted_rels.csv")
    
    # check that fetch_articles_from_atlas was called
    mock_connector.fetch_articles_from_atlas.assert_called_once_with(query={})
    
    # check NLP processing methods were called
    assert mock_nlp.extract_and_normalize_entities.call_count == 2
    assert mock_nlp.extract_relations.call_count == 2
    mock_nlp.generate_entities_csv.assert_called_once()
    mock_nlp.generate_relations_csv.assert_called_once()

def test_annotate_mongo_articles_keyboard_interrupt(mock_connector, mock_normalizer, mock_nlp, caplog):
    # simulate KeyboardInterrupt on first call
    def interrupt(*args, **kwargs):
        raise KeyboardInterrupt

    mock_nlp.extract_and_normalize_entities.side_effect = interrupt

    with patch("scripts.transform.annotate.MongoAtlasConnector", return_value=mock_connector), \
         patch("scripts.transform.annotate.UMLSNormalizer", return_value=mock_normalizer), \
         patch("scripts.transform.annotate.NLP", return_value=mock_nlp), \
         patch("tqdm.tqdm", lambda x: x), \
         caplog.at_level(logging.ERROR):

        annotate_module.annotate_mongo_articles(ents_path="fake_extracted_ents.csv", rels_path="fake_extracted_rels.csv")

    # error log must contain the interruption message
    assert any("Annotation Process Interrupted Manually." in record.message for record in caplog.records)
    
    # finally block should still call CSV generation
    mock_nlp.generate_entities_csv.assert_called_once()
    mock_nlp.generate_relations_csv.assert_called_once()

def test_annotate_mongo_articles_empty_articles(mock_connector, mock_normalizer, mock_nlp):
    # simulate no articles returned
    mock_connector.fetch_articles_from_atlas.return_value = []

    with patch("scripts.transform.annotate.MongoAtlasConnector", return_value=mock_connector), \
         patch("scripts.transform.annotate.UMLSNormalizer", return_value=mock_normalizer), \
         patch("scripts.transform.annotate.NLP", return_value=mock_nlp), \
         patch("tqdm.tqdm", lambda x: x):
        
        annotate_module.annotate_mongo_articles(ents_path="fake_extracted_ents.csv", rels_path="fake_extracted_rels.csv")

    # no processing methods should be called
    mock_nlp.extract_and_normalize_entities.assert_not_called()
    mock_nlp.extract_relations.assert_not_called()
    
    # CSV generation should still run
    mock_nlp.generate_entities_csv.assert_called_once()
    mock_nlp.generate_relations_csv.assert_called_once()
