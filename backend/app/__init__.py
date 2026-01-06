from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os

db = SQLAlchemy()

def create_app():
    # Load env variables
    load_dotenv()

    app = Flask(__name__)

    # CORS configuration - allow all origins for development
    CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # Database config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Register all blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    with app.app_context():
        from app import models  # <-- IMPORTANT: ensure models are imported
        from app.models import TransitNode, Business  # Import all models
        db.create_all()         # Create DB tables

    return app
