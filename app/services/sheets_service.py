import base64
import json
import logging
import gspread
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

    def _ensure_connected(self):
        """Ensure the service is connected to Google Sheets"""
        if not self.client or not self.spreadsheet or not self.worksheet:
            self._connect()

    def _connect(self):
        """Connect to Google Sheets Client"""
        try:
            scopes = current_app.config['SCOPES']  
            credentials_base64 = current_app.config['GOOGLE_SHEETS_CREDENTIALS_BASE64']

            # Load credentials from JSON file
            try:
                credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
                credentials_dict = json.loads(credentials_json)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON format for Google Sheets credentials: {e}")
                return

            creds = Credentials.from_service_account_info(
                credentials_dict,
                scopes=scopes
            )

            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(current_app.config['GOOGLE_SHEETS_ID'])
            self.worksheet = self.spreadsheet.get_worksheet(0)
            logger.info("Successfully connected to Google Sheets")

        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            self.client = None
            self.spreadsheet = None
            self.worksheet = None
            raise
    
    def add_lead(self, lead: Lead) -> bool:
        """Add a lead to Google Sheets"""
        try:
            # Ensure we are connected to Google Sheets
            self._ensure_connected()

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