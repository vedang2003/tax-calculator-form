import logging
import os
from flask import Flask
from config import config
from app.extensions import csrf

def create_app(config_name='default'):
    """Application factory pattern"""
    # Get the directory where this file is located (app/)
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    app = Flask(__name__, 
                template_folder=os.path.join(app_dir, 'templates'),
                static_folder=os.path.join(app_dir, 'static'))
    
    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    return app