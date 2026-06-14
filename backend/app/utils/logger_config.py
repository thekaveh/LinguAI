import logging
import os
from datetime import datetime

log_setup_completed = False

def setup_global_logging(logger_name='LinguAI-BACKEND', log_filename='/app/logs/backend-app.log', log_level="ERROR"):
    global log_setup_completed
    
    # Check if logging setup has already been completed
    if not log_setup_completed:
        # Append a timestamp to the base filename for each container start
        start_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        formatted_log_filename = os.path.join(os.path.dirname(log_filename), f"{os.path.basename(log_filename)}_{start_timestamp}")

        # Set up file handler
        file_handler = logging.FileHandler(formatted_log_filename)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)

        # Fetch and configure the named logger
        logger = logging.getLogger(logger_name)
        numeric_level = logging.getLevelName(log_level.upper())
        logger.setLevel(numeric_level)
        logger.addHandler(file_handler)
        
        # Set flag to indicate logging setup completion
        log_setup_completed = True
