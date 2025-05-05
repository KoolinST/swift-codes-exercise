import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from app.data_parser import parse_swift_codes

@pytest.fixture
def mock_bank_class():
    with patch("app.data_parser.Bank") as MockBank:
        yield MockBank

@pytest.fixture
def mock_db_session():
    with patch("app.extensions.db.session") as mock_db:
        yield mock_db

def test_parse_swift_codes_success(mock_bank_class, mock_db_session):
    test_data = pd.DataFrame([
        {
            "SWIFT CODE": "EXAMPLEXXX",
            "ADDRESS": "TODOR ALEKSANDROV BLVD 73 FLOOR 1 SOFIA, SOFIA, 1303",
            "NAME": "BANK POLSKA",
            "COUNTRY ISO2 CODE": "PL",
            "COUNTRY NAME": "POLAND"
        }
    ])

    with patch("app.data_parser.pd.read_csv", return_value=test_data):
        mock_bank_instance = MagicMock()
        mock_bank_class.return_value = mock_bank_instance
        mock_bank_class.query.filter_by.return_value.first.return_value = None

        result = parse_swift_codes("dummy.csv")

        assert len(result) == 1
        mock_db_session.add.assert_called_once_with(mock_bank_instance)
        mock_db_session.commit.assert_called_once()

def test_parse_swift_codes_branch_no_hq(mock_bank_class, mock_db_session):
    test_data = pd.DataFrame([
        {
            "SWIFT CODE": "EXAMPLEXXX",
            "ADDRESS": "TODOR ALEKSANDROV BLVD 73 FLOOR 1 SOFIA, SOFIA, 1303",
            "NAME": "BANK POLSKA",
            "COUNTRY ISO2 CODE": "PL",
            "COUNTRY NAME": "POLAND"
        }
    ])

    with patch("app.data_parser.pd.read_csv", return_value=test_data):
        mock_bank_instance = MagicMock()
        mock_bank_class.return_value = mock_bank_instance
        mock_bank_class.query.filter_by.return_value.first.return_value = None

        result = parse_swift_codes("dummy.csv")

        bank_arg = mock_bank_class.call_args[1]
        assert bank_arg["associated_headquarter"] is None


def test_parse_swift_codes_updates_existing_bank(mock_bank_class, mock_db_session):
    test_data = pd.DataFrame([
        {
            "SWIFT CODE": "EXAMPLEXXX",
            "ADDRESS": "TODOR ALEKSANDROV BLVD 73 FLOOR 1 SOFIA, SOFIA, 1303",
            "NAME": "BANK POLSKA",
            "COUNTRY ISO2 CODE": "PL",
            "COUNTRY NAME": "POLAND"
        }
    ])

    existing_bank = MagicMock()
    existing_bank.address = "OLD ADDRESS"
    existing_bank.bank_name = "OLD BANK"
    existing_bank.country_iso2 = "PL"
    existing_bank.country_name = "POLAND"
    mock_bank_class.query.filter_by.return_value.first.return_value = existing_bank

    with patch("app.data_parser.pd.read_csv", return_value=test_data):
        parse_swift_codes("dummy.csv")

        existing_bank.address = "KOSZYKARSKA"
        existing_bank.bank_name = "BANK PL"
        existing_bank.country_iso2 = "PL"
        existing_bank.country_name = "POLAND"

        assert existing_bank.address == "KOSZYKARSKA"
        assert existing_bank.bank_name == "BANK PL"
        assert existing_bank.country_iso2 == "PL"
        assert existing_bank.country_name == "POLAND"
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_called_once()


def test_parse_swift_codes_read_csv_error(mock_bank_class, mock_db_session):
    with patch("app.data_parser.pd.read_csv", side_effect=Exception("File not found")):
        result = parse_swift_codes("invalid.csv")
        assert result == []
        mock_db_session.add.assert_not_called()

def test_parse_swift_codes_db_commit_fails(mock_bank_class, mock_db_session):
    test_data = pd.DataFrame([
        {
            "SWIFT CODE": "IJKLFR99XXX",
            "ADDRESS": "99 Champs-Élysées",
            "NAME": "Bank IJKL",
            "COUNTRY ISO2 CODE": "fr",
            "COUNTRY NAME": "France"
        }
    ])

    mock_db_session.commit.side_effect = Exception("DB down")

    with patch("app.data_parser.pd.read_csv", return_value=test_data):
        result = parse_swift_codes("dummy.csv")

        assert result != []
        mock_db_session.rollback.assert_called_once()