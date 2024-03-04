import functools
import logging
import time

def log_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Debug: Log detailed argument values
        args_repr = [repr(a) for a in args]  # Representational string of args
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # Representational string of kwargs
        function_arguments = ", ".join(args_repr + kwargs_repr)
        logging.debug(f"Calling {func.__name__}() with {function_arguments}")
        logging.info(f"Entering: {func.__name__}")        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()

            # Info: Log function execution and duration at a higher level
            logging.info(f"{func.__name__}() executed in {end_time - start_time:.4f} seconds")

            # Debug: Log function result
            logging.debug(f"{func.__name__}() returned {result!r}")
            return result
        except Exception as e:
            end_time = time.time()
            logging.error(f"Error in {func.__name__}() after {end_time - start_time:.4f} seconds: {e}", exc_info=True)
            raise
    return wrapper
