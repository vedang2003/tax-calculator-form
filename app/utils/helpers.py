def format_proper_case(value: str) -> str:
    """Format string to proper case"""
    if not value:
        return value
    return value.replace('-', ' ').title()

def sanitize_phone_number(phone: str) -> str:
    """Sanitize phone number input"""
    if not phone:
        return ""
    # Keep only digits, +, -, (, ), and spaces
    import re
    return re.sub(r'[^\d+\-\(\)\s]', '', phone.strip())