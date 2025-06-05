import base64
import json
import logging
import gspread
import time
from google.oauth2.service_account import Credentials
from flask import current_app
from app.models.lead import Lead

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    """Service for managing Google Sheets operations"""
    
    def __init__(self):
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        self._connect()

    def _connect(self):
        """Connect to Google Sheets Client"""

        try:
            # Check if we're in an application context
            if not current_app:
                logger.error("No Flask application context available")
                return
                
            logger.info("Starting _connect() method")
            
            scopes = current_app.config['SCOPES']  
            credentials_base64 = current_app.config['GOOGLE_SHEETS_CREDENTIALS_BASE64']

            if not credentials_base64:
                logger.error("GOOGLE_SHEETS_CREDENTIALS_BASE64 not found in config")
                return

            # Decode credentials
            try:
                credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
                credentials_dict = json.loads(credentials_json)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON format for Google Sheets credentials: {e}")
                return
            except Exception as e:
                logger.error(f"Error decoding credentials: {e}")
                return

            # Create credentials and connect
            creds = Credentials.from_service_account_info(
                credentials_dict,
                scopes=scopes
            )

            logger.info("Authorizing Google Sheets client")
            time.sleep(1)  
            self.client = gspread.authorize(creds)
            if not self.client:
                logger.error("Failed to authorize Google Sheets client")
                return
            logger.info("Successfully authorized Google Sheets client")

            time.sleep(1)
            self.spreadsheet = self.client.open_by_key(current_app.config['GOOGLE_SHEETS_ID'])
            if not self.spreadsheet:
                logger.error("Failed to open Google Sheets spreadsheet")
                return
            logger.info(f"Connected to Google Sheets spreadsheet: {self.spreadsheet.title}")

            self.worksheet = self.spreadsheet.get_worksheet(0)
            logger.info("Successfully connected to Google Sheets")

        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            self.client = None
            self.spreadsheet = None
            self.worksheet = None
    
    def add_lead(self, lead: Lead) -> bool:
        """Add a lead to Google Sheets"""
        try:
            if not self.client or not self.worksheet:
                logger.error("Google Sheets not connected")
                return False
            
            # Add the lead data
            self.worksheet.append_row(lead.to_sheets_row())
            logger.info(f"Added lead to Google Sheets: {lead.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add lead to Google Sheets: {e}")
            return False