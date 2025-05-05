from flask import jsonify, abort, request, Response
from app.models.bank import Bank
from app.extensions import db
import logging
import json


logger = logging.getLogger(__name__)


def register_routes(app):
    @app.route("/v1/swift-codes/<string:swift_code>", methods=["GET"])
    def get_swift_code_details(swift_code):
        swift_code = swift_code.upper()
        bank = Bank.query.filter_by(swift_code=swift_code).first()
        if not bank:
            abort(404, description="SWIFT code not found")

        base_response = {
            "address": bank.address,
            "bankName": bank.bank_name,
            "countryISO2": bank.country_iso2,
            "countryName": bank.country_name,
            "isHeadquarter": bank.is_headquarter,
            "swiftCode": bank.swift_code
        }

        if bank.is_headquarter:
            branches = Bank.query.filter_by(associated_headquarter=swift_code).all()
            base_response["branches"] = [
                {
                    "address": b.address,
                    "bankName": b.bank_name,
                    "countryISO2": b.country_iso2,
                    "isHeadquarter": b.is_headquarter,
                    "swiftCode": b.swift_code
                }
                for b in branches
            ]

        return Response(json.dumps(base_response,
                                   indent=4,
                                   sort_keys=False), mimetype="application/json")

    @app.route("/v1/swift-codes/country/<string:country_iso2>", methods=["GET"])
    def get_swift_codes_by_country(country_iso2):
        country_iso2 = country_iso2.upper()
        banks = Bank.query.filter_by(country_iso2=country_iso2).all()
        if not banks:
            abort(404, description="No SWIFT codes found for the specified country")
        country_name = banks[0].country_name if banks else ""
        return jsonify({
            "countryISO2": country_iso2,
            "countryName": country_name,
            "swiftCodes": [
                {
                    "swiftCode": bank.swift_code,
                    "address": bank.address,
                    "bankName": bank.bank_name,
                    "countryISO2": bank.country_iso2,
                    "isHeadquarter": bank.is_headquarter
                }
                for bank in banks
            ]
        })

    @app.route("/v1/swift-codes", methods=["POST"])
    def add_swift_code():
        data = request.get_json(force=True)

        required_fields = [
            "swiftCode", "address", "bankName",
            "countryISO2", "countryName", "isHeadquarter"
        ]

        for field in required_fields:
            if field not in data:
                abort(400, description=f"Missing field: {field}")

        swift_code = data["swiftCode"].upper()
        if Bank.query.filter_by(swift_code=swift_code).first():
            abort(409, description="SWIFT code already exists")

        try:

            new_bank = Bank(
                swift_code=swift_code,
                address=data["address"],
                bank_name=data["bankName"],
                country_iso2=data["countryISO2"].upper(),
                country_name=data["countryName"].upper(),
                is_headquarter=data["isHeadquarter"]
            )

            db.session.add(new_bank)
            db.session.commit()

            return jsonify({
                "message": f"SWIFT code, with value {swift_code} added successfully"
            }), 201

        except Exception as e:
            db.session.rollback()
            logger.error(f"Internal error during SWIFT code creation: {e}")
            abort(500, description="Internal Server Error")

    @app.route("/v1/swift-codes/<string:swift_code>", methods=["DELETE"])
    def delete_swift_code(swift_code):
        swift_code = swift_code.upper()
        bank = Bank.query.filter_by(swift_code=swift_code).first()

        if not bank:
            abort(404, description="SWIFT code not found")
        try:
            db.session.delete(bank)
            db.session.commit()

            return jsonify({
                "message": f"SWIFT code, with value {swift_code} deleted successfully"
            }), 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Internal error during SWIFT code deletion: {e}")
            abort(500, description="Internal Server Error")

    @app.errorhandler(404)
    def handle_404_error(error):
        description = getattr(error, "description", "Not Found")
        return jsonify({"message": description}), 404

    @app.errorhandler(400)
    def handle_400_error(error):
        description = getattr(error, "description", "Bad Request")
        return jsonify({"message": description}), 400

    @app.errorhandler(409)
    def handle_409_error(error):
        description = getattr(error, "description", "Conflict")
        return jsonify({"message": description}), 409

    @app.errorhandler(500)
    def handle_500_error(error):
        return jsonify({"message": "Internal Server Error"}), 500
