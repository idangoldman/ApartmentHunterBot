from flask import Flask, jsonify
from .database import init_app
import os
from dotenv import load_dotenv
from etc.fb_scraper import  get_env_path
from pymongo.errors import PyMongoError
from pymongo import MongoClient
from .extensions import socketio  # Import socketio from extensions.py
from celery import Celery # type: ignore

# Load the .env file
load_dotenv(dotenv_path=get_env_path())

# Celery configuration
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend='redis://localhost:6379/0',  # Using Redis as backend
        broker='redis://localhost:6379/0'    # Using Redis as broker
    )
    
    celery.conf.update(app.config)
    return celery



def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config["MONGO_URI"] = os.getenv(key="MONGO_URL")
    
    # Initialize MongoClient once and store it in app.config
    app.config['MONGO_CLIENT'] = MongoClient(os.getenv(key="MONGO_URL"))

    # Initialize SocketIO with the app
    # socketio.init_app(app)

    # Register Blueprints or routes here
    from . import routes
    app.register_blueprint(blueprint=routes.bp)

    # Initialize the database
    init_app(app)
    
    # Middleware to handle PyMongo exceptions
    @app.errorhandler(code_or_exception=PyMongoError)
    def handle_pymongo_error(error):
        app.logger.error(f"Database error: {error}")
        return jsonify({"status": "error", "message": "A database error occurred."}), 500

    return app
