from flask import Flask
from app.extensions import db
from app.routes import register_routes
import os
from dotenv import load_dotenv


load_dotenv()


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    db_user = os.getenv('POSTGRES_USER', 'remitly')
    db_password = os.getenv('POSTGRES_PASSWORD', 'remitly')
    db_host = os.getenv('DB_HOST', 'localhost' if config_name == 'testing' else 'db')
    db_name = os.getenv('POSTGRES_DB', 'swift_data_test' if config_name == 'testing' else 'swift_data')
    database_uri = f'postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}'
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = config_name == 'testing'

    db.init_app(app)
    register_routes(app)

    return app
