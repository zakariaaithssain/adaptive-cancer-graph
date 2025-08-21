import pytest
from unittest.mock import patch, Mock

from modules.pubmed_api import PubMedAPI

# ------------------------
# Fixtures
# ------------------------

@pytest.fixture
def pubmed():
    return PubMedAPI(api_key="dummy_key", email="test@example.com")

@pytest.fixture
def sample_search_response():
    return {
        "esearchresult": {
            "count": "1",
            "webenv": "WE123",
            "querykey": "QK456",
            "idlist": ["12345"]
        }
    }

@pytest.fixture
def sample_fetch_response_xml():
    xml_content = """
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>12345</PMID>
                <Article>
                    <ArticleTitle>Sample Title</ArticleTitle>
                    <Abstract>
                        <AbstractText>Sample abstract text</AbstractText>
                    </Abstract>
                    <MeshHeadingList>
                        <MeshHeading>
                            <DescriptorName>SampleMesh</DescriptorName>
                        </MeshHeading>
                    </MeshHeadingList>
                    <KeywordList>
                        <Keyword>keyword1</Keyword>
                    </KeywordList>
                    <ArticleIdList>
                        <ArticleId IdType="pmc">PMC12345</ArticleId>
                    </ArticleIdList>
                </Article>
            </MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>
    """
    mock_resp = Mock()
    mock_resp.text = xml_content
    mock_resp.status_code = 200
    return mock_resp

# ------------------------
# Tests for search()
# ------------------------

@patch("modules.pubmed_api.rq.post")
@patch("modules.pubmed_api.time.sleep", return_value=None)
@patch("modules.pubmed_api.logging")
def test_search_success(mock_logging, mock_sleep, mock_post, pubmed, sample_search_response):
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = sample_search_response
    mock_post.return_value = mock_resp

    result = pubmed.search(query="cancer", max_results=5)
    assert result == sample_search_response
    assert pubmed.search_results_count == int(sample_search_response["esearchresult"]["count"])
    mock_post.assert_called_once()
    mock_sleep.assert_called_once()  # Ensure sleep is called

@patch("modules.pubmed_api.rq.post")
@patch("modules.pubmed_api.time.sleep", return_value=None)
@patch("modules.pubmed_api.logging")
def test_search_failure(mock_logging, mock_sleep, mock_post, pubmed):
    mock_resp = Mock()
    mock_resp.status_code = 500
    mock_post.return_value = mock_resp

    result = pubmed.search(query="cancer")
    assert result is None
    mock_post.assert_called_once()
    mock_sleep.assert_not_called()  # sleep should not run on failure

# ------------------------
# Tests for fetch()
# ------------------------

@patch("modules.pubmed_api.rq.post")
@patch("modules.pubmed_api.time.sleep", return_value=None)
@patch("modules.pubmed_api.logging")
def test_fetch_pubmed_success(mock_logging, mock_sleep, mock_post, pubmed, sample_search_response, sample_fetch_response_xml):
    mock_post.return_value = sample_fetch_response_xml
    fetch_response = pubmed.fetch(search_data=sample_search_response)
    assert fetch_response == sample_fetch_response_xml
    mock_post.assert_called_once()
    mock_sleep.assert_called_once()

# ------------------------
# Tests for get_data_from_xml()
# ------------------------

def test_get_data_from_xml(pubmed, sample_fetch_response_xml):
    articles = pubmed.get_data_from_xml(sample_fetch_response_xml)
    assert len(articles) == 1
    article = articles[0]
    assert article["pmid"] == "12345"
    assert article["pmcid"] == "12345"
    assert article["title"] == "Sample Title"
    assert article["abstract"] == "Sample abstract text"
    assert article["medical_subject_headings"] == ["SampleMesh"]
    assert article["keywords"] == ["keyword1"]
