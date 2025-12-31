"""
Configuration management for TextAI Studio.
Loads environment variables with validation.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""

    # Application
    APP_NAME = os.getenv('APP_NAME', 'TextAI Studio')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    APP_ENV = os.getenv('APP_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '8501'))

    # Storage
    DATA_DIR = Path(os.getenv('DATA_DIR', './user_data'))
    HISTORY_DIR = Path(os.getenv('HISTORY_DIR', './user_data/history'))
    UPLOAD_DIR = Path(os.getenv('UPLOAD_DIR', './user_data/uploads'))
    MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', '10'))

    # Models
    MODEL_CACHE_DIR = Path(os.getenv('MODEL_CACHE_DIR', './models'))
    SENTIMENT_MODEL = os.getenv('SENTIMENT_MODEL', 'distilbert-base-uncased-finetuned-sst-2-english')
    SUMMARIZER_MODEL = os.getenv('SUMMARIZER_MODEL', 'facebook/bart-large-cnn')
    FAKE_NEWS_MODEL = os.getenv('FAKE_NEWS_MODEL', 'bert-base-uncased')
    JOB_MATCHER_MODEL = os.getenv('JOB_MATCHER_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')

    # Performance
    ENABLE_MODEL_CACHE = os.getenv('ENABLE_MODEL_CACHE', 'true').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL', '300'))
    MAX_BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', '100'))

    # Rate Limiting
    GUEST_RATE_LIMIT = int(os.getenv('GUEST_RATE_LIMIT', '10'))
    USER_RATE_LIMIT = int(os.getenv('USER_RATE_LIMIT', '100'))
    PRO_RATE_LIMIT = int(os.getenv('PRO_RATE_LIMIT', '1000'))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = Path(os.getenv('LOG_FILE', './logs/app.log'))

    # Feature Flags
    ENABLE_USER_SIGNUP = os.getenv('ENABLE_USER_SIGNUP', 'true').lower() == 'true'
    ENABLE_API_ACCESS = os.getenv('ENABLE_API_ACCESS', 'true').lower() == 'true'
    ENABLE_BATCH_PROCESSING = os.getenv('ENABLE_BATCH_PROCESSING', 'true').lower() == 'true'
    ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'true').lower() == 'true'
    ENABLE_ADMIN_DASHBOARD = os.getenv('ENABLE_ADMIN_DASHBOARD', 'true').lower() == 'true'

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        errors = []

        if not cls.SECRET_KEY:
            errors.append("SECRET_KEY is required")

        if not cls.ADMIN_PASSWORD:
            errors.append("ADMIN_PASSWORD is required")

        if cls.APP_ENV == 'production' and cls.DEBUG:
            errors.append("DEBUG should be false in production")

        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")

    @classmethod
    def create_directories(cls):
        """Create required directories."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.HISTORY_DIR.mkdir(exist_ok=True)
        cls.UPLOAD_DIR.mkdir(exist_ok=True)
        cls.MODEL_CACHE_DIR.mkdir(exist_ok=True)
        cls.LOG_FILE.parent.mkdir(exist_ok=True)

# Validate on import
Config.validate()
