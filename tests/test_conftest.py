import pytest
from app.extensions import db
from app import create_app
from app.models.bank import Bank
from flask import json
from unittest.mock import patch


@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()


def test_get_swift_code_details(client):
    bank = Bank(
        swift_code="AVJCBGS1XXX",
        address="TODOR ALEKSANDROV BLVD 73 FLOOR 1 SOFIA, SOFIA, 1303",
        bank_name="AVAL IN JSC",
        country_iso2="BG",
        country_name="BULGARIA",
        is_headquarter=True,
    )
    with client.application.app_context():
        db.session.add(bank)
        db.session.commit()

    response = client.get("/v1/swift-codes/AVJCBGS1XXX")

    assert response.status_code == 200
    data = response.get_json()
    assert data["swiftCode"] == "AVJCBGS1XXX"
    assert data["address"] == "TODOR ALEKSANDROV BLVD 73 FLOOR 1 SOFIA, SOFIA, 1303"
    assert data["isHeadquarter"] is True


def test_get_swift_code_details_not_found(client):
    response = client.get("/v1/swift-codes/NONEXISTENTCODE")
    assert response.status_code == 404
    data = response.get_json()
    assert data["message"] == "SWIFT code not found"


def test_get_swift_codes_by_country(client):
    bank1 = Bank(
        swift_code="AVJCBGS1XXX",
        address="TODOR ALEKSANDROV BLVD 73 FLOOR 1 SOFIA, SOFIA, 1303",
        bank_name="AVAL IN JSC",
        country_iso2="BG",
        country_name="BULGARIA",
        is_headquarter=True,
    )
    bank2 = Bank(
        swift_code="ATISMTM1XXX",
        address="TODOR ALEKSANDROV BLVD 73 FLOOR 1 SOFIA, SOFIA, 1303",
        bank_name="AVAL IN JSC",
        country_iso2="BG",
        country_name="BULGARIA",
        is_headquarter=False,
    )

    with client.application.app_context():
        db.session.add(bank1)
        db.session.add(bank2)
        db.session.commit()

    response = client.get("/v1/swift-codes/country/BG")

    assert response.status_code == 200

    data = response.get_json()

    assert data["countryISO2"] == "BG"
    assert data["countryName"] == "BULGARIA"
    assert len(data["swiftCodes"]) == 2
    assert data["swiftCodes"][0]["swiftCode"] == "AVJCBGS1XXX"
    assert data["swiftCodes"][1]["swiftCode"] == "ATISMTM1XXX"


def test_get_swift_codes_by_country_not_found(client):
    response = client.get("/v1/swift-codes/country/ZZ")
    assert response.status_code == 404
    data = response.get_json()
    assert data["message"] == "No SWIFT codes found for the specified country"


def test_add_swift_code_success(client):
    bank = {
        "swiftCode": "EXAMPLEXXX",
        "address": "TODOR ALEKSANDROV BLVD 73 FLOOR 1 SOFIA, SOFIA, 1303",
        "bankName": "BANK POLSKA",
        "countryISO2": "PL",
        "countryName": "POLAND",
        "isHeadquarter": True,
    }

    response = client.post(
        "/v1/swift-codes", data=json.dumps(bank), content_type="application/json"
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert "SWIFT code, with value EXAMPLEXXX added successfully" in data["message"]


def test_add_swift_code_missing_field(client):
    bank = {
        "swiftCode": "EXAMPLEXXX",
        "address": "TODOR ALEKSANDROV BLVD 73 FLOOR 1 SOFIA, SOFIA, 1303",
        "bankName": "BANK POLSKA",
        "countryISO2": "PL",
        "isHeadquarter": True,
    }


    response = client.post(
        "/v1/swift-codes", data=json.dumps(bank), content_type="application/json"
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "Missing field: countryName" in data["message"]


def test_add_swift_code_duplicate(client):
    bank = Bank(
        swift_code="EXAMPLEXXX",
        address="TODOR ALEKSANDROV BLVD 73 FLOOR 1 SOFIA, SOFIA, 1303",
        bank_name="BANK POLSKA",
        country_iso2="PL",
        country_name="POLAND",
        is_headquarter=True,
    )
    with client.application.app_context():
        db.session.add(bank)
        db.session.commit()

    bank2 = {
        "swiftCode": "EXAMPLEXXX",
        "address": "TODOR ALEKSANDROV BLVD 73 FLOOR 1 SOFIA, SOFIA, 1303",
        "bankName": "BANK POLSKA",
        "countryISO2": "PL",
        "countryName": "POLAND",
        "isHeadquarter": False,
    }


    response = client.post(
        "/v1/swift-codes", data=json.dumps(bank2), content_type="application/json"
    )

    assert response.status_code == 409
    data = json.loads(response.data)
    assert "SWIFT code already exists" in data["message"]


@patch("app.routes.db.session.commit", side_effect=Exception("DB Error"))
def test_add_swift_code_db_error(mock_commit, client):
    bank = {
        "swiftCode": "EXAMPLEXXX",
        "address": "TODOR ALEKSANDROV BLVD 73 FLOOR 1 SOFIA, SOFIA, 1303",
        "bankName": "BANK POLSKA",
        "countryISO2": "PL",
        "countryName": "POLAND",
        "isHeadquarter": False,
    }

    response = client.post(
        "/v1/swift-codes", data=json.dumps(bank), content_type="application/json"
    )

    assert response.status_code == 500
    data = json.loads(response.data)
    assert "Internal Server Error" in data["message"]


def test_delete_swift_code_success(client):
    bank = Bank(
        swift_code="EXAMPLEXXX",
        address="TODOR ALEKSANDROV BLVD 73 FLOOR 1 SOFIA, SOFIA, 1303",
        bank_name="BANK POLSKA",
        country_iso2="PL",
        country_name="POLAND",
        is_headquarter=True,
    )
    with client.application.app_context():
        db.session.add(bank)
        db.session.commit()

    response = client.delete("/v1/swift-codes/EXAMPLEXXX")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "SWIFT code, with value EXAMPLEXXX deleted successfully" in data["message"]

    with client.application.app_context():
        assert Bank.query.filter_by(swift_code="EXAMPLEXXX").first() is None


def test_delete_swift_code_not_found(client):
    response = client.delete("/v1/swift-codes/DOESNOTEXIST")

    assert response.status_code == 404
    data = json.loads(response.data)
    assert "SWIFT code not found" in data["message"]


@patch("app.routes.db.session.delete", side_effect=Exception("Simulated failure"))
def test_delete_swift_code_internal_error(mock_delete, client):
    bank = Bank(
        swift_code="EXAMPLEXXX",
        address="TODOR ALEKSANDROV BLVD 73 FLOOR 1 SOFIA, SOFIA, 1303",
        bank_name="BANK POLSKA",
        country_iso2="PL",
        country_name="POLAND",
        is_headquarter=False,
    )
    with client.application.app_context():
        db.session.add(bank)
        db.session.commit()

    response = client.delete("/v1/swift-codes/EXAMPLEXXX")

    assert response.status_code == 500
    data = json.loads(response.data)
    assert "Internal Server Error" in data["message"]
