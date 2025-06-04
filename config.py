# Configuration file for the application
import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""   
    SECRET_KEY = secrets.token_hex(16)  # Generate a secure random secret key
    
    # Google Sheets Configuration
    GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID')  
    GOOGLE_SHEETS_CREDENTIALS_BASE64 = os.getenv('GOOGLE_SHEETS_CREDENTIALS_BASE64')
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    # Email configuration
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')  
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD') 

    # Tax calculator file path
    TAX_CALCULATOR_FILE = 'tax_calculator.xlsx'  

    # Rate limiting configuration
    RATE_LIMIT_MAX_REQUESTS = 5  
    RATE_LIMIT_TIME_WINDOW_MINUTES = 10 

    # CSRF Configuration
    WTF_CSRF_TIME_LIMIT = 3600
    WTF_CSRF_SSL_STRICT = False

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    WTF_CSRF_SSL_STRICT = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}