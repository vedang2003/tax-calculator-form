from collections import defaultdict
from datetime import datetime, timedelta
from flask import current_app

# Simple in-memory rate limiting (use Redis for production)
submission_tracker = defaultdict(list)

def is_rate_limited(ip_address: str) -> bool:
    """Check if IP address is rate limited"""
    max_requests = current_app.config.get('RATE_LIMIT_MAX_REQUESTS',5)
    time_window_minutes = current_app.config.get('RATE_LIMIT_TIME_WINDOW_MINUTES', 10)
    
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

def clear_rate_limit_cache():
    """Clear rate limiting cache (useful for testing)"""
    submission_tracker.clear()