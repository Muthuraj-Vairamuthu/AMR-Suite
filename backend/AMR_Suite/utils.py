import logging
import json
from datetime import datetime
from django.conf import settings
import os

# Configure logging
logging.basicConfig(
    filename=os.path.join(settings.BASE_DIR, 'audit.log'),
    level=logging.INFO,
    format='[%(asctime)s] [%(event_type)s] [user:%(user)s] %(message)s'
)

def log_event(event_type, user, description, details_dict=None):
    """
    Logs an event in both human-readable and machine-readable formats.
    
    Args:
        event_type (str): The type of event (e.g., UPLOAD, VALIDATE, MAP).
        user (str): The username or session ID of the user.
        description (str): A human-readable description of the event.
        details_dict (dict, optional): Additional details for machine-readable logging.
    """
    # Human-readable log
    logging.info(
        f"{description}",
        extra={'event_type': event_type, 'user': user}
    )
    
    # Machine-readable log (JSON)
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "user": user,
        "description": description,
        "details": details_dict or {}
    }
    
    with open(os.path.join(settings.BASE_DIR, 'audit.json'), 'a') as f:
        f.write(json.dumps(log_entry) + '\n') 