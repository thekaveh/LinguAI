import logging
import logging.handlers
from queue import Queue
import os
import shutil
from datetime import datetime
import glob

def setup_global_logging(logger_name='LinguAI-BACKEND', log_filename='/app/logs/backend-app.log', log_level="INFO"):
    """
    Set up global logging configuration.

    Args:
        logger_name (str, optional): The name of the logger. Defaults to 'LinguAI-BACKEND'.
        log_filename (str, optional): The path and filename of the log file. Defaults to '/app/logs/backend-app.log'.
        log_level (str, optional): The log level. Defaults to 'INFO'.

    Returns:
        None
    """
    log_directory = os.path.dirname(log_filename)
    base_filename = os.path.basename(log_filename)
    base_filename_without_ext, ext = os.path.splitext(base_filename)

    archive_directory = os.path.join(log_directory, "archive")

    # Create archive directory if it doesn't exist
    if not os.path.exists(archive_directory):
        os.makedirs(archive_directory)

    # Move existing log files to archive directory before setting up new logging
    existing_log_files = glob.glob(os.path.join(log_directory, f"{base_filename_without_ext}_*{ext}"))
    for existing_log_file in existing_log_files:
        archive_file_path = os.path.join(archive_directory, os.path.basename(existing_log_file))
        if os.path.exists(archive_file_path):
            # If the file exists, append a unique identifier to avoid conflict
            base, extension = os.path.splitext(archive_file_path)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            new_archive_file_path = f"{base}_{timestamp}{extension}"
            shutil.move(existing_log_file, new_archive_file_path)
        else:
            shutil.move(existing_log_file, archive_directory)

    # Append a timestamp to the base filename for each container start
    start_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    formatted_log_filename = os.path.join(log_directory, f"{base_filename_without_ext}_{start_timestamp}{ext}")

    log_queue = Queue(-1)  # No limit on size
    
    # Use TimedRotatingFileHandler for rotating logs every half hour and keep for 1 week
    file_handler = logging.handlers.TimedRotatingFileHandler(
        formatted_log_filename, 
        when="M", 
        interval=30, 
        backupCount=336)  # 48 segments per day * 7 days = 336 segments
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)

    queue_handler = logging.handlers.QueueHandler(log_queue)
    queue_listener = logging.handlers.QueueListener(log_queue, file_handler)

    # Fetch and configure the named logger
    logger = logging.getLogger(logger_name)
    numeric_level = logging.getLevelName(log_level.upper())
    logger.setLevel(numeric_level)
    logger.addHandler(queue_handler)

    queue_listener.start()

    import atexit
    atexit.register(queue_listener.stop)