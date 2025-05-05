import pandas as pd
import logging
from app.models.bank import Bank
from app.extensions import db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_swift_codes(filename):
    cleaned_data = []

    try:
        df = pd.read_csv(filename)

        df["COUNTRY ISO2 CODE"] = df["COUNTRY ISO2 CODE"].str.upper()
        df["COUNTRY NAME"] = df["COUNTRY NAME"].str.upper()
        df = df.drop(columns=['CODE TYPE', 'TOWN NAME', 'TIME ZONE'], errors='ignore')

        logger.info("File successfully read and cleaned.")

    except Exception as e:
        logger.error(f"Error while reading CSV file: {e}")
        return []

    try:
        for _, row in df.iterrows():
            swift_code = row['SWIFT CODE'].upper()
            is_headquarter = swift_code.endswith("XXX")
            associated_hq = None

            if not is_headquarter:
                associated_hq = swift_code[:8] + "XXX"
                if df[df['SWIFT CODE'].str.upper() == associated_hq].empty:
                    associated_hq = None

            bank = Bank(
                swift_code=swift_code,
                address=row['ADDRESS'],
                bank_name=row['NAME'],
                country_iso2=row['COUNTRY ISO2 CODE'],
                country_name=row['COUNTRY NAME'],
                is_headquarter=is_headquarter,
                associated_headquarter=associated_hq
            )

            cleaned_data.append(bank)

            existing_bank = Bank.query.filter_by(swift_code=swift_code).first()
            if existing_bank:
                existing_bank.address = bank.address
                existing_bank.bank_name = bank.bank_name
                existing_bank.country_iso2 = bank.country_iso2
                existing_bank.country_name = bank.country_name
                existing_bank.is_headquarter = bank.is_headquarter
                existing_bank.associated_headquarter = bank.associated_headquarter
            else:
                db.session.add(bank)

        db.session.commit()
        logger.info("Data inserted successfully.")

    except Exception as e:
        logger.error(f"Database error: {e}")
        db.session.rollback()

    return cleaned_data
