"""Service for uploading videos to a MiniIO database with additional metadata stored in a PostgreSQL database."""
from flask import Flask
from flask_cors import CORS

from .routes import api
from .models.video_metadata import db


def create_app():
    app = Flask(__name__)

    # TODO: Configure CORS correctly.
    CORS(app, resources={r"/*": {"origins": "http://localhost:5003"}})

    # Connection to PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@postgres:5432/videos'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.register_blueprint(api)

    with app.app_context():
        # Create the tables if they don't exist
        db.create_all()

    return app
