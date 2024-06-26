import time
import logging
import functools

from core.config import Config


def log_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Use the same logger name as configured globally
        logger = logging.getLogger(Config.FRONTEND_LOGGER_NAME)
        logger.debug(
            f"Function {func.__name__} called with args: {args} and kwargs: {kwargs}"
        )
        logger.info(f"Entering function: {func.__name__}")

        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Function {func.__name__} returned {result}")
            return result
        except Exception as e:
            logger.exception(
                f"Exception occurred in function {func.__name__}: {str(e)}"
            )
            raise  # Re-raise the exception after logging
        finally:
            end_time = time.time()
            logger.info(
                f"Exiting function: {func.__name__}, Execution time: {end_time - start_time:.4f} seconds"
            )

    return wrapper
