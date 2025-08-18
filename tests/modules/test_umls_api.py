import pytest
from unittest.mock import patch, Mock
from modules.umls_api import UMLSNormalizer  # adjust import path

# ------------------------
# Fixtures
# ------------------------
@pytest.fixture
def normalizer():
    return UMLSNormalizer()

# ------------------------
# Test successful normalization
# ------------------------
@patch("modules.umls_api.time.sleep")  # avoid actual sleeping
@patch("modules.umls_api.rq.get")      # mock requests.get
def test_normalize_success(mock_get, mock_sleep, normalizer):
    # Mock the API JSON response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "result": {
            "results": [
                {
                    "ui": "C0000001",
                    "name": "Human",
                    "rootSource": "UMLS",
                    "uri": "https://example.com/C0000001"
                }
            ]
        }
    }
    mock_get.return_value = mock_response

    result = normalizer.normalize("human")

    # Check the returned dict keys
    assert result["cui"] == "C0000001"
    assert result["normalized_name"] == "Human"
    assert result["normalization_source"] == "UMLS"
    assert result["url"] == "https://example.com/C0000001"

    # Ensure requests.get was called with correct parameters
    mock_get.assert_called_once()
    called_args, called_kwargs = mock_get.call_args
    assert "human" in called_kwargs["params"]["string"]

# ------------------------
# Test empty results
# ------------------------
@patch("modules.umls_api.time.sleep")
@patch("modules.umls_api.rq.get")
def test_normalize_no_results(mock_get, mock_sleep, normalizer):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": {"results": []}}
    mock_get.return_value = mock_response

    result = normalizer.normalize("unknown term")
    assert result == {}

# ------------------------
# Test result with "ui" == "NONE"
# ------------------------
@patch("modules.umls_api.time.sleep")
@patch("modules.umls_api.rq.get")
def test_normalize_ui_none(mock_get, mock_sleep, normalizer):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "result": {"results": [{"ui": "NONE", "name": "None"}]}
    }
    mock_get.return_value = mock_response

    result = normalizer.normalize("invalid")
    assert result == {}

# ------------------------
# Test non-200 status code
# ------------------------
@patch("modules.umls_api.time.sleep")
@patch("modules.umls_api.rq.get")
def test_normalize_error_status(mock_get, mock_sleep, normalizer):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    result = normalizer.normalize("error")
    assert result == {}
