import os
from app import create_app

# Create Flask app
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)