import logging
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import current_app
from app.models.lead import Lead

logger = logging.getLogger(__name__)

class EmailService:
    """Service for email operations"""
    
    def __init__(self):
        self.smtp_server = current_app.config['SMTP_SERVER']
        self.smtp_port = current_app.config['SMTP_PORT']
        self.email_address = current_app.config['EMAIL_ADDRESS']
        self.email_password = current_app.config['EMAIL_PASSWORD']
    
    def send_tax_calculator(self, lead: Lead) -> bool:
        """Send tax calculator email with attachment"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = lead.email
            msg['Subject'] = "Your Tax Calculator is Ready!"
            
            # Email body
            body = self._get_email_body(lead.full_name)
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach Excel file
            if not self._attach_tax_calculator(msg):
                return False
            
            # Send email
            self._send_email(msg, lead.email)
            logger.info(f"Email sent successfully to {lead.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {lead.email}: {e}")
            return False
    
    def _get_email_body(self, recipient_name: str) -> str:
        """Get email body template"""
        return f"""
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
    
    def _attach_tax_calculator(self, msg: MIMEMultipart) -> bool:
        """Attach tax calculator file to email"""
        file_path = current_app.config['TAX_CALCULATOR_FILE']
        
        if not os.path.exists(file_path):
            logger.error(f"Tax calculator file not found: {file_path}")
            return False
        
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="Tax_Calculator_2025.xlsx"'
            )
            msg.attach(part)
            return True
            
        except Exception as e:
            logger.error(f"Failed to attach file: {e}")
            return False
    
    def _send_email(self, msg: MIMEMultipart, recipient_email: str):
        """Send the email"""
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        server.login(self.email_address, self.email_password)
        server.sendmail(self.email_address, recipient_email, msg.as_string())
        server.quit()