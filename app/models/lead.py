from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Lead:
    """Lead data model"""
    full_name: str
    email: str
    phone: Optional[str] = ""
    state: Optional[str] = ""
    district: Optional[str] = ""
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'fullName': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'state': self.state,
            'district': self.district,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def to_sheets_row(self):
        """Convert to Google Sheets row format"""
        return [
            self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else "",
            self.full_name,
            self.email,
            self.phone,
            self.state,
            self.district
        ]
    
    @classmethod
    def from_form_data(cls, form_data):
        """Create Lead from form data"""
        return cls(
            full_name=form_data.get('fullName', '').strip(),
            email=form_data.get('email', '').strip().lower(),
            phone=form_data.get('phone', '').strip(),
            state=form_data.get('state', '').strip(),
            district=form_data.get('district', '').strip()
        )