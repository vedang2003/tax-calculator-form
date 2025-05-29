from flask import Flask, request, render_template, jsonify, send_from_directory
import gspread
from google.oauth2.service_account import Credentials
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
import logging
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

app = Flask(
    __name__,
    static_folder='static',      
    template_folder='templates'  
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')  # Your Gmail address
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # Your app password
GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID')  # Your Google Sheet ID
CREDENTIALS_FILE = 'credentials.json'  # Path to your service account credentials
TAX_CALCULATOR_FILE = 'tax_calculator.xlsx'  # Path to your Excel file

# Simple in-memory rate limiting (use Redis for production)
submission_tracker = defaultdict(list)

def is_rate_limited(ip_address, max_requests=5, time_window_minutes=10):
    now = datetime.now()
    cutoff = now - timedelta(minutes=time_window_minutes)
    
    # Clean old entries
    submission_tracker[ip_address] = [
        timestamp for timestamp in submission_tracker[ip_address] 
        if timestamp > cutoff
    ]
    
    # Check if limit exceeded
    if len(submission_tracker[ip_address]) >= max_requests:
        return True
    
    # Add current request
    submission_tracker[ip_address].append(now)
    return False

class GoogleSheetsHandler:
    def __init__(self):
        self.client = None
        self.sheet = None
        self._connect()
    
    def _connect(self):
        try:
            creds = Credentials.from_service_account_file(
                CREDENTIALS_FILE, scopes=SCOPES
            )
            self.client = gspread.authorize(creds)
            spreadsheet = self.client.open_by_key(GOOGLE_SHEETS_ID)
            self.sheet = spreadsheet.get_worksheet(0) 
            logger.info("Successfully connected to Google Sheets")
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            raise
    
    def add_lead(self, data):
        try:
            # Prepare row data
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row_data = [
                timestamp,
                data.get('fullName', ''),
                data.get('email', ''),
                data.get('phone', ''),
                data.get('state', ''),
                data.get('district', '')
            ]
            
            # Add headers if sheet is empty
            if not self.sheet.get_all_records():
                headers = ['Timestamp', 'Full Name', 'Email', 'Phone', 'State', 'District']
                self.sheet.insert_row(headers, index=1)
                logger.info("Added headers to empty sheet")
            
            # Add the lead data
            self.sheet.append_row(row_data)
            logger.info(f"Added lead to Google Sheets: {data.get('email')}")
            return True
        except Exception as e:
            logger.error(f"Failed to add lead to Google Sheets: {e}")
            return False

class EmailHandler:
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.email_address = EMAIL_ADDRESS
        self.email_password = EMAIL_PASSWORD
    
    def send_tax_calculator_attachment(self, recipient_email, recipient_name):
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = recipient_email
            msg['Subject'] = "Your Tax Calculator is Ready!"
            
            # Email body with download link
            body = f"""
            Hi {recipient_name},
            
            Thank you for requesting our free tax calculator! 
            📎 Your tax calculator Excel file is attached to this email.

            
            This comprehensive Excel spreadsheet will help you:
            ✓ Calculate your estimated tax liability
            ✓ Track deductions and credits
            ✓ Plan for next year's taxes
            ✓ Organize your financial information
            
            The spreadsheet is easy to use - just fill in your information in the highlighted cells and the formulas will do the rest!
            
            📋 How to use:
            1. Download the attachment from this email
            2. Save the file to your computer
            3. Open in Excel or Google Sheets
            4. Follow the instructions in the first tab
            
            If you have any questions or need tax planning assistance, feel free to reply to this email.
            
            Best regards,
            Tax Calculator Team
            """
            
            msg.attach(MIMEText(body, 'plain'))

            # Attach the Excel file
            if os.path.exists(TAX_CALCULATOR_FILE):
                with open(TAX_CALCULATOR_FILE, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= "Tax_Calculator_2025.xlsx"'
                )
                msg.attach(part)
            else:
                logger.error(f"Tax calculator file not found: {TAX_CALCULATOR_FILE}")
                return False
            
            # Send email (no attachment needed!)
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_address, recipient_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {e}")
            return False

# Initialize handlers
sheets_handler = GoogleSheetsHandler()
email_handler = EmailHandler()

@app.route('/')
def index():
    # Serve the HTML file
    return render_template('index.html')



@app.route('/submit', methods=['POST'])
def submit_form():
    # Rate limiting
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    if is_rate_limited(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return jsonify({'error': 'Too many requests. Please try again later.'}), 429
    
    try:
        def format_proper_case(value):
            if not value:
                return value
            return value.replace('-', ' ').title()
        
        # Get form data
        form_data = {
            'fullName': request.form.get('fullName'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone', ''),
            'state': format_proper_case(request.form.get('state', '')),
            'district': format_proper_case(request.form.get('district', ''))
        }
        
        # Validate required fields
        if not form_data['fullName'] or not form_data['email']:
            return jsonify({'error': 'Name and email are required'}), 400
        
        # Add to Google Sheets
        sheets_success = sheets_handler.add_lead(form_data)
        
        # Send email with attachment
        email_success = email_handler.send_tax_calculator_attachment(
            form_data['email'], 
            form_data['fullName']
        )
        
        if sheets_success and email_success:
            logger.info(f"Successfully processed lead: {form_data['email']}")
            return jsonify({'message': 'Success'}), 200
        else:
            logger.error(f"Partial failure processing lead: {form_data['email']}")
            return jsonify({'error': 'Partial failure'}), 500
            
    except Exception as e:
        logger.error(f"Error processing form submission: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Check if required files exist
    required_files = [CREDENTIALS_FILE, TAX_CALCULATOR_FILE]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        logger.error(f"Missing required files: {missing_files}")
        print("Please ensure the following files exist:")
        for file in missing_files:
            print(f"  - {file}")
    else:
        logger.info("Starting Flask application...")
        app.run(debug=True, host='0.0.0.0', port=5500)