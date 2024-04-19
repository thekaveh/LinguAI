import time
import logging
import functools

from app.core.config import Config


def log_decorator(func):
    """
    A decorator function that logs the entry, exit, and any exceptions that occur within the decorated function.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.

    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Use the same logger name as configured globally
        logger = logging.getLogger(Config.BACKEND_LOGGER_NAME)
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
