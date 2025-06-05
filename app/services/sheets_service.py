import base64
import sys
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
        self._connect()

    def _connect(self):
        """Connect to Google Sheets Client"""

        try:
            logger.info("Starting _connect() method")
            
            scopes = current_app.config['SCOPES']  
            credentials_base64 = current_app.config['GOOGLE_SHEETS_CREDENTIALS_BASE64']
            sheet_id = current_app.config['GOOGLE_SHEETS_ID']

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
            
            # Set recursion limit temporarily to catch infinite loops
            original_recursion_limit = sys.getrecursionlimit()
            sys.setrecursionlimit(100)  # Much lower limit to catch issues early
            
            try:
                self.client = gspread.authorize(creds)
                logger.info("Google Sheets client authorized successfully")
                
                # This is where the recursion often happens - add extra protection
                self.spreadsheet = self.client.open_by_key(sheet_id)
                logger.info(f"Spreadsheet opened: {self.spreadsheet.title}")

                self.worksheet = self.spreadsheet.get_worksheet(0)
                logger.info(f"Worksheet obtained: {self.worksheet.title}")
                
                self._connection_successful = True
                logger.info("Successfully connected to Google Sheets")
                
            finally:
                # Restore original recursion limit
                sys.setrecursionlimit(original_recursion_limit)

        except RecursionError as e:
            logger.error(f"Recursion error in Google Sheets connection: {e}")

        except gspread.SpreadsheetNotFound as e:
            logger.error(f"Spreadsheet not found: {e}")

        except gspread.exceptions.APIError as e:
            logger.error(f"Google Sheets API error: {e}")
        
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
    
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