import logging
import gspread
from google.oauth2.service_account import Credentials
from flask import current_app
from app.models.lead import Lead

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    """Service for Google Sheets operations"""
    
    def __init__(self):
        self.client = None
        self.sheet = None
        self._connect()
    
    def _connect(self):
        """Connect to Google Sheets"""
        try:
            creds = Credentials.from_service_account_file(
                current_app.config['CREDENTIALS_FILE'], 
                scopes=current_app.config['SCOPES']
            )
            self.client = gspread.authorize(creds)
            spreadsheet = self.client.open_by_key(current_app.config['GOOGLE_SHEETS_ID'])
            self.sheet = spreadsheet.get_worksheet(0)
            logger.info("Successfully connected to Google Sheets")
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            raise
    
    def add_lead(self, lead: Lead) -> bool:
        """Add a lead to Google Sheets"""
        try:
            if not self.sheet:
                logger.error("Sheet not connected")
                return False
            
            # Add the lead data
            self.sheet.append_row(lead.to_sheets_row())
            logger.info(f"Added lead to Google Sheets: {lead.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add lead to Google Sheets: {e}")
            return False