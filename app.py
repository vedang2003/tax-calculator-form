import os
from app import create_app

# Create Flask app
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # Check if required files exist (development only)
    if config_name == 'development':
        required_files = [
            app.config['CREDENTIALS_FILE'], 
            app.config['TAX_CALCULATOR_FILE']
        ]
        missing_files = [f for f in required_files if not os.path.exists(f)]

        if missing_files:
            print("Missing required files:")
            for file in missing_files:
                print(f"  - {file}")
            exit(1)
    
    # Run the application
    port = int(os.getenv('PORT', 5500))
    print(f"Starting Flask application in {config_name} mode on port {port}")
    app.run(debug=(config_name == 'development'), host='0.0.0.0', port=port)