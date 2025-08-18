import pytest
from unittest.mock import patch, MagicMock
import logging
import os 

from scripts.load import load_to_aura


@pytest.fixture
def mock_connector():
    mock = MagicMock()
    mock.__enter__.return_value = mock  # for the context manager
    mock.__exit__.return_value = None
    return mock


@pytest.mark.parametrize(
    "labels_to_load, ents_csv, reltypes_to_load, rels_csv, should_raise",
    [
        (None, None, None, None, True),             # no args -> should raise
        (["Label"], "ents.csv", None, None, False), # only nodes -> ok
        (None, None, ["REL"], "rels.csv", False),   # only rels -> ok
        (["Label"], "ents.csv", ["REL"], "rels.csv", False), # both -> ok
    ]
)
def test_load_to_aura_args_validation(labels_to_load, ents_csv, reltypes_to_load, rels_csv, should_raise):
    if should_raise:
        with pytest.raises(ValueError):
            load_to_aura(labels_to_load, ents_csv, reltypes_to_load, rels_csv)
    else:
        # Patch the connector where it is imported in scripts.load
        with patch("scripts.load.Neo4jAuraConnector") as mock_class:
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None
            mock_class.return_value = mock_instance

            load_to_aura(labels_to_load, ents_csv, reltypes_to_load, rels_csv)

            if labels_to_load and ents_csv:
                mock_instance.load_ents_to_aura.assert_called_once_with(labels_to_load, ents_csv)
            if reltypes_to_load and rels_csv:
                mock_instance.load_rels_to_aura.assert_called_once_with(reltypes_to_load, rels_csv)


def test_load_to_aura_keyboard_interrupt(caplog):
    with patch("scripts.load.Neo4jAuraConnector") as mock_class:
        mock_instance = MagicMock()
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.__exit__.return_value = None
        mock_instance.load_ents_to_aura.side_effect = KeyboardInterrupt
        mock_class.return_value = mock_instance

        caplog.set_level(logging.ERROR)
        load_to_aura(["Label"], "ents.csv")
        assert any("Load Process Interrupted Manually." in r.message for r in caplog.records)


def test_load_to_aura_exception_logging(caplog):
    with patch("scripts.load.Neo4jAuraConnector") as mock_class:
        mock_instance = MagicMock()
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.__exit__.return_value = None
        mock_instance.load_ents_to_aura.side_effect = RuntimeError("DB failure")
        mock_class.return_value = mock_instance

        caplog.set_level(logging.ERROR)
        load_to_aura(["Label"], "ents.csv")
        assert any("Load Process Failed To Load To Aura." in r.message for r in caplog.records)


if os.path.exists("fake_ents.csv"):
        os.remove("fake_ents.csv")
if os.path.exists("fake_rels.csv"):
        os.remove("fake_rels.csv")