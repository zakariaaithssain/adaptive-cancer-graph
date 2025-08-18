import pytest
from unittest.mock import patch, Mock
from xml.etree import ElementTree as ET

from modules.pubmedcentral_api import PubMedCentralAPI

# ------------------------
# Fixtures
# ------------------------

@pytest.fixture
def pmc_api():
    return PubMedCentralAPI(api_key="dummy_key", email="test@example.com")

@pytest.fixture
def sample_full_article_xml():
    xml_content = """
    <article>
        <body>
            <p>First paragraph of the article.</p>
            <p>Second paragraph of the article.</p>
        </body>
    </article>
    """
    mock_resp = Mock()
    mock_resp.text = xml_content
    return mock_resp

@pytest.fixture
def sample_article_no_body_xml():
    xml_content = "<article></article>"
    mock_resp = Mock()
    mock_resp.text = xml_content
    return mock_resp

# ------------------------
# Test get_data_from_xml()
# ------------------------

@patch("modules.pubmedcentral_api.logging")
def test_get_data_from_xml_success(mock_logging, pmc_api, sample_full_article_xml):
    # Mock the inherited search and fetch methods
    pmc_api.search = Mock(return_value="dummy_search_result")
    pmc_api.fetch = Mock(return_value=sample_full_article_xml)

    content = pmc_api.get_data_from_xml("PMC12345")
    expected_content = "First paragraph of the article.\n\nSecond paragraph of the article."
    assert content == expected_content

    pmc_api.search.assert_called_once_with(db="pmc", pmc_id="PMC12345", rettype="full")
    pmc_api.fetch.assert_called_once_with("dummy_search_result", db="pmc", pmc_id="PMC12345", rettype="full")

@patch("modules.pubmedcentral_api.logging")
def test_get_data_from_xml_no_body(mock_logging, pmc_api, sample_article_no_body_xml):
    pmc_api.search = Mock(return_value="dummy_search_result")
    pmc_api.fetch = Mock(return_value=sample_article_no_body_xml)

    content = pmc_api.get_data_from_xml("PMC67890")
    assert content is None

@patch("modules.pubmedcentral_api.logging")
def test_get_data_from_xml_fetch_none(mock_logging, pmc_api):
    pmc_api.search = Mock(return_value="dummy_search_result")
    pmc_api.fetch = Mock(return_value=None)

    content = pmc_api.get_data_from_xml("PMC00000")
    assert content is None

# ------------------------
# Optional: parametrize different paragraph scenarios
# ------------------------

@pytest.mark.parametrize(
    "xml_text,expected",
    [
        ("<article><body><p>Single paragraph</p></body></article>", "Single paragraph"),
        ("<article><body><p>Para1</p><p>Para2</p><p>Para3</p></body></article>", "Para1\n\nPara2\n\nPara3"),
        ("<article></article>", None),
    ]
)
@patch("modules.pubmedcentral_api.logging")
def test_get_data_from_xml_various(mock_logging, pmc_api, xml_text, expected):
    mock_resp = Mock()
    mock_resp.text = xml_text

    pmc_api.search = Mock(return_value="dummy")
    pmc_api.fetch = Mock(return_value=mock_resp)

    result = pmc_api.get_data_from_xml("PMCXXXX")
    assert result == expected
