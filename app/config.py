"""Initialize Config class to access environment variables."""
from dotenv import load_dotenv
import os

load_dotenv()

class Config(object):
    """Set environment variables."""

    # Use SQLite by default if no DATABASE_URL is provided
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///culinaryconnect.db")
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-for-development-only')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
