# logging_config.py
import logging
import logging.handlers
from queue import Queue

def setup_global_logging(logger_name='LinguAI', log_filename='/app/logs/frontend-app.log', log_level="INFO"):
    log_queue = Queue(-1)
    file_handler = logging.FileHandler(log_filename)
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
