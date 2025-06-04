import logging
from flask import Blueprint, request, jsonify
from app.models.lead import Lead
from app.services.sheets_service import GoogleSheetsService
from app.services.email_service import EmailService
from app.utils.rate_limiting import is_rate_limited
from app.utils.helpers import format_proper_case

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

@api_bp.route('/submit', methods=['POST'])
def submit_form():
    """Handle form submission"""

    # Rate limiting
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    if is_rate_limited(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return jsonify({'error': 'Too many requests. Please try again later.'}), 429
    
    try:
         # Debug: Log the raw form data
        logger.info(f"Raw form data: {dict(request.form)}")
        
        # Create lead from form data
        form_data = {
            'fullName': request.form.get('fullName', ''),
            'email': request.form.get('email', ''),
            'phone': request.form.get('phone', ''),
            'state': format_proper_case(request.form.get('state', '')),
            'district': format_proper_case(request.form.get('district', ''))
        }
        
        # Debug: Log the processed form data
        logger.info(f"Processed form data: {form_data}")
        
        lead = Lead.from_form_data(form_data)
        
        # Validate required fields
        if not lead.full_name or not lead.email:
            logger.error(f"Missing required fields - Name: {lead.full_name}, Email: {lead.email}")
            return jsonify({'error': 'Name and email are required'}), 400
        
        # Initialize services with error handling
        try:
            sheets_service = GoogleSheetsService()
            sheets_success = sheets_service.add_lead(lead)
        except Exception as e:
            logger.error(f"Sheets service failed: {e}")
            sheets_success = False
        
        try:
            email_service = EmailService()
            email_success = email_service.send_tax_calculator(lead)
        except Exception as e:
            logger.error(f"Email service failed: {e}")
            email_success = False
        
        if sheets_success and email_success:
            logger.info(f"Successfully processed lead: {lead.full_name}")
            return jsonify({'message': 'Success'}), 200
        else:
            logger.error(f"Partial failure processing lead: {lead.full_name}")
            return jsonify({'error': 'Service temporarily unavailable'}), 500
            
    except Exception as e:
        logger.error(f"Error processing form submission: {e}")
        return jsonify({'error': 'Internal server error'}), 500