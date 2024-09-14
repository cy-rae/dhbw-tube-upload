"""Service for uploading videos to a MiniIO database with additional metadata stored in a PostgreSQL database."""
from flask import Flask
from flask_cors import CORS

from app.models.video_metadata import db
from app.routes.health_check_routes import health_check_api
from app.routes.upload_routes import upload_api


def create_app():
    app = Flask(__name__)

    CORS(app, resources={r"/*": {"origins": "http://frontend-service"}})

    # Connection to PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@postgres:5432/videos'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Register blueprints
    app.register_blueprint(upload_api)
    app.register_blueprint(health_check_api)

    with app.app_context():
        # Create the tables if they don't exist
        db.create_all()

    return app
