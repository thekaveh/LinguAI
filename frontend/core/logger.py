import logging
import sys


def setup_logging(logger_name: str, log_level: str = "INFO", log_file: str | None = None) -> logging.Logger:
    """Configure a named logger with a stdout handler (and optional file handler)."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s — %(message)s")
    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(fmt)
    logger.addHandler(stdout)

    if log_file:
        try:
            fh = logging.FileHandler(log_file)
            fh.setFormatter(fmt)
            logger.addHandler(fh)
        except OSError:
            logger.warning("Could not open log file %s; continuing with stdout only", log_file)

    logger.propagate = False
    return logger
