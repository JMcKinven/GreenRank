# backend/config.py
"""
Configuration for Flask app and database connection.
Uses environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Database configuration
DB_USER = os.getenv("DB_USER", "greenrank_user")
DB_PASS = os.getenv("DB_PASS", "greenrank_pass")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "greenrank")

# Build SQLAlchemy URI
SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask config
DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
