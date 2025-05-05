from app import db


class Bank(db.Model):
    __tablename__ = 'banks'

    swift_code = db.Column(db.String(11), primary_key=True)
    address = db.Column(db.Text)
    bank_name = db.Column(db.String(255))
    country_iso2 = db.Column(db.String(2))
    country_name = db.Column(db.String(255))
    is_headquarter = db.Column(db.Boolean)
    associated_headquarter = db.Column(db.String(11), nullable=True)
