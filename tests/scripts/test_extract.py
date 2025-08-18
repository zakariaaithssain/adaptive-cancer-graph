import pytest
import logging
from unittest.mock import Mock, patch

import scripts.extract as extraction   


# -----------------
# FIXTURES
# -----------------
@pytest.fixture
def mock_pubmed_api():
    mock = Mock()
    mock.search.return_value = "search_results"
    mock.search_results_count = 3
    mock.fetch.return_value = "<xml>"
    mock.get_data_from_xml.return_value = [
        {"pmcid": "PMC123", "title": "Test article"}
    ]
    return mock

@pytest.fixture
def mock_pubmedcentral_api():
    mock = Mock()
    mock.get_data_from_xml.return_value = "full article text"
    return mock

@pytest.fixture
def mock_mongo_connector():
    return Mock()


# -----------------
# TESTS FOR _get_data_from_apis
# -----------------
@pytest.mark.parametrize("abstracts_only", [True, False])
def test_get_data_from_apis_handles_results(
    mock_pubmed_api, mock_pubmedcentral_api, abstracts_only
):
    articles = extraction._get_data_from_apis(
        pubmed_api=mock_pubmed_api,
        pubmedcentral_api=mock_pubmedcentral_api,
        extract_abstracts_only=abstracts_only,
        max_results=2
    )

    assert isinstance(articles, list)
    assert "title" in articles[0]
    if abstracts_only:
        # No full body requested
        assert "body" not in articles[0]
    else:
        # Body should be added
        assert articles[0]["body"] == "full article text"


def test_get_data_from_apis_respects_max_results(mock_pubmed_api, mock_pubmedcentral_api):
    mock_pubmed_api.search_results_count = 5
    articles = extraction._get_data_from_apis(
        mock_pubmed_api, mock_pubmedcentral_api, max_results=1
    )
    # Should paginate until all articles fetched
    assert len(articles) > 0
    assert mock_pubmed_api.fetch.call_count > 1


# -----------------
# TESTS FOR extract_pubmed_to_mongo
# -----------------
def test_extract_pubmed_to_mongo_loads_articles(
    mock_pubmed_api, mock_pubmedcentral_api, mock_mongo_connector
):
    with patch.object(extraction, "pubmed_api", mock_pubmed_api), \
         patch.object(extraction, "pubmedcentral_api", mock_pubmedcentral_api), \
         patch.object(extraction, "mongo_connector", mock_mongo_connector):

        extraction.extract_pubmed_to_mongo(extract_abstracts_only=True, max_results=2)

        mock_mongo_connector.load_articles_to_atlas.assert_called_once()
        args, kwargs = mock_mongo_connector.load_articles_to_atlas.call_args
        assert isinstance(args[0], list)
        assert kwargs["abstract_only"] is True


def test_extract_pubmed_to_mongo_keyboard_interrupt(
    mock_pubmed_api, mock_pubmedcentral_api, mock_mongo_connector, caplog
):
    # Force _get_data_from_apis to raise KeyboardInterrupt
    with patch.object(extraction, "_get_data_from_apis", side_effect=KeyboardInterrupt):
        with caplog.at_level(logging.ERROR):
            extraction.extract_pubmed_to_mongo()

    assert "Extraction Process Interrupted Manually." in caplog.text


# -----------------
# NEGATIVE / EDGE CASES
# -----------------
def test_get_data_from_apis_returns_empty_if_no_results(mock_pubmed_api, mock_pubmedcentral_api):
    mock_pubmed_api.get_data_from_xml.return_value = []
    mock_pubmed_api.search_results_count = 0

    articles = extraction._get_data_from_apis(
        mock_pubmed_api, mock_pubmedcentral_api, max_results=1
    )

    assert articles == []


def test_get_data_from_apis_invalid_params(mock_pubmed_api, mock_pubmedcentral_api):
    with pytest.raises(TypeError):
        extraction._get_data_from_apis(
            pubmed_api=mock_pubmed_api  # missing pubmedcentral_api argument
        )
