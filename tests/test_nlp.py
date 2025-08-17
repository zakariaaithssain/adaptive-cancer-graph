import pytest
import pandas as pd
from unittest.mock import Mock, patch

import modules.umls_api as umls_api
import config.nlp_config as nlp_config
from modules.nlp import NLP

# -------------------
# Fixtures
# -------------------

@pytest.fixture
def mock_normalizer():
    normalizer = Mock(spec=umls_api.UMLSNormalizer)
    normalizer.normalize.side_effect = lambda text: {"cui": f"CUI_{text}", "normalized_name": text.upper()}
    return normalizer

import spacy
from spacy.vocab import Vocab

@pytest.fixture
def mock_spacy_model():
    from spacy.vocab import Vocab
    vocab = Vocab()
    vocab.strings.add("RELATES_TO")
    vocab.strings.add("ASSOCIATED_WITH")

    # fake ents
    ent1 = Mock(text="GeneX", label_="GENE", start=0, end=1)
    ent2 = Mock(text="CancerY", label_="DISEASE", start=1, end=2)

    # fake tokens for dependency matches
    token1 = Mock(text="GeneX")
    token2 = Mock(text="CancerY")

    class FakeDoc(list):
        def __init__(self):
            super().__init__([token1, token2])
            self.ents = [ent1, ent2]

    fake_doc = FakeDoc()

    mock_nlp = Mock()
    mock_nlp.return_value = fake_doc
    mock_nlp.vocab = vocab
    mock_nlp.add_pipe = Mock()
    mock_nlp.get_pipe = Mock(return_value=Mock(labels=["GENE", "DISEASE"]))
    return mock_nlp



@pytest.fixture(autouse=True)
def patch_spacy_load(mock_spacy_model):
    with patch("modules.nlp.spacy.load", return_value=mock_spacy_model):
        yield

@pytest.fixture(autouse=True)
def patch_matcher_patterns():
    with patch.object(nlp_config, "MATCHER_PATTERNS", {"RELATES_TO": [[{"LOWER": "genex"}]]}):
        with patch.object(nlp_config, "DEPENDENCY_MATCHER_PATTERNS", {"ASSOCIATED_WITH": [[{"RIGHT_ID": "foo"}]]}):
            yield


# -------------------
# Tests
# -------------------

def test_extract_entities(mock_normalizer):
    nlp = NLP(normalizer=mock_normalizer)
    article_meta = {"pmid": "123"}
    
    nlp.extract_and_normalize_entities("GeneX causes CancerY", article_meta)
    
    assert len(nlp.entities) == 2
    assert all("cui" in e for e in nlp.entities)
    assert all(e["pmid"] == "123" for e in nlp.entities)

@pytest.mark.parametrize("matches, dep_matches, expected_count", [
    ([(111, 0, 2)], [], 1),           # Matcher finds one relation
    ([], [(222, [0, 1])], 1),         # Dependency matcher finds one relation
    ([(111, 0, 2)], [(222, [0, 1])], 2), # Both find relations
])
def test_extract_relations(mock_normalizer, matches, dep_matches, expected_count):
    nlp = NLP(normalizer=mock_normalizer)
    nlp.matcher = Mock(return_value=matches)
    nlp.dep_matcher = Mock(return_value=dep_matches)

    article_meta = {"pmid": "123"}
    nlp.extract_relations("GeneX causes CancerY", article_meta)
    
    assert len(nlp.relations) == expected_count
    assert all(r["pmid"] == "123" for r in nlp.relations)


def test_generate_entities_csv_success(tmp_path, mock_normalizer):
    nlp = NLP(normalizer=mock_normalizer)
    nlp.entities = [{"text": "genex", "label": "GENE"}]

    file_path = tmp_path / "entities.csv"
    nlp.generate_entities_csv(file_path)

    df = pd.read_csv(file_path)
    assert "text" in df.columns
    assert df.iloc[0]["text"] == "genex"


def test_generate_relations_csv_success(tmp_path, mock_normalizer):
    nlp = NLP(normalizer=mock_normalizer)
    nlp.relations = [{"ent1": "genex", "relation": "RELATES_TO", "ent2": "cancery"}]

    file_path = tmp_path / "relations.csv"
    nlp.generate_relations_csv(file_path)

    df = pd.read_csv(file_path)
    assert "ent1" in df.columns
    assert df.iloc[0]["ent1"] == "genex"


def test_generate_entities_csv_failure(monkeypatch, mock_normalizer):
    nlp = NLP(normalizer=mock_normalizer)
    nlp.entities = [{"text": "genex", "label": "GENE"}]

    class FakeDF:
        def to_csv(self, *_, **__):
            raise IOError("disk full")

    monkeypatch.setattr("pandas.DataFrame", lambda *_, **__: FakeDF())

    # should not raise, just log error
    result = nlp.generate_entities_csv("fake.csv")
    assert isinstance(result, NLP)


def test_no_entities_or_relations(mock_normalizer, tmp_path):
    nlp = NLP(normalizer=mock_normalizer)

    ent_file = tmp_path / "ents.csv"
    rel_file = tmp_path / "rels.csv"

    nlp.generate_entities_csv(ent_file)
    df1 = pd.read_csv(ent_file)
    assert df1.empty or "entity" in df1.columns

    nlp.generate_relations_csv(rel_file)
    df2 = pd.read_csv(rel_file)
    assert df2.empty or "ent1" in df2.columns
