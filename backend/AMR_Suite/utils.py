import logging
import json
import os
from datetime import datetime
from django.conf import settings

# Set up logging directories if they don't exist
LOG_DIR = os.path.join(settings.BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'audit.log'),
    level=logging.INFO,
    format='[%(asctime)s] [%(event_type)s] [user:%(user)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger('audit_logger')

def log_event(event_type, user, description, details_dict=None):
    """Log events in both human-readable and machine-readable formats"""
    try:
        # Human-readable log
        logger.info(
            description,
            extra={
                'event_type': event_type,
                'user': user
            }
        )

        # Machine-readable log (JSON)
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user": user,
            "description": description,
            "details": details_dict or {}
        }

        json_log_path = os.path.join(LOG_DIR, 'audit.json')
        
        # Append to JSON file
        try:
            if os.path.exists(json_log_path):
                with open(json_log_path, 'r+') as f:
                    try:
                        logs = json.load(f)
                        if not isinstance(logs, list):
                            logs = []
                    except json.JSONDecodeError:
                        logs = []
            else:
                logs = []

            logs.append(log_entry)

            with open(json_log_path, 'w') as f:
                json.dump(logs, f, indent=2)

        except Exception as e:
            print(f"Error writing to JSON log: {str(e)}")
            logger.error(f"Failed to write to JSON log: {str(e)}")

    except Exception as e:
        print(f"Error in log_event: {str(e)}")
        logging.error(f"Logging failed: {str(e)}")