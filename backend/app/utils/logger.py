import time
import inspect
import logging
import functools

from app.core.config import Config


# Field names whose value must never be logged, even on debug. Matching is
# substring + case-insensitive so e.g. "current_password", "new_password",
# and "password_hash" are all covered. Used by `_redact()` below.
_SENSITIVE_FIELD_SUBSTRINGS = (
    "password",
    "secret",
    "token",
    "api_key",
)


def _redact(value: object) -> object:
    """Return ``value`` with any sensitive Pydantic/SQLModel/dict fields masked.

    The logger previously emitted ``args``/``kwargs`` verbatim, which meant
    plaintext passwords from login/signup/change-password requests landed in
    the backend log. This helper masks any field whose name contains one of
    the substrings above while keeping the rest of the payload visible for
    debugging.
    """
    # Pydantic v2 / v1 models expose `model_dump` or `dict`.
    dump_fn = getattr(value, "model_dump", None) or getattr(value, "dict", None)
    if callable(dump_fn):
        try:
            data = dump_fn()
        except Exception:
            return f"<{type(value).__name__}>"
        if isinstance(data, dict):
            return {k: ("<redacted>" if _is_sensitive(k) else _redact(v)) for k, v in data.items()}
        return data
    if isinstance(value, dict):
        return {k: ("<redacted>" if _is_sensitive(str(k)) else _redact(v)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        kind = type(value)
        return kind(_redact(v) for v in value)
    return value


def _is_sensitive(field_name: str) -> bool:
    lowered = field_name.lower()
    return any(substr in lowered for substr in _SENSITIVE_FIELD_SUBSTRINGS)


def log_decorator(func):
    """Logs entry, exit, and exceptions for the decorated function.

    Args and kwargs are redacted via ``_redact`` so that requests carrying
    passwords/tokens do not surface their plaintext in the application log.

    Works for both sync and ``async def`` callables: when ``func`` is a
    coroutine function the wrapper awaits it, so the measured execution time
    reflects the real async work and exceptions raised inside the coroutine
    are logged. A sync wrapper around an async function would instead time
    only coroutine *creation* and never see its exceptions.
    """

    def _log_entry(args, kwargs):
        logger = logging.getLogger(Config.BACKEND_LOGGER_NAME)
        if logger.isEnabledFor(logging.DEBUG):
            safe_args = tuple(_redact(a) for a in args)
            safe_kwargs = {k: ("<redacted>" if _is_sensitive(k) else _redact(v)) for k, v in kwargs.items()}
            logger.debug(
                "Function %s called with args: %r and kwargs: %r",
                func.__name__,
                safe_args,
                safe_kwargs,
            )
        logger.info("Entering function: %s", func.__name__)
        return logger

    def _log_result(logger, result):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Function %s returned %r", func.__name__, _redact(result))

    def _log_exit(logger, start_time):
        logger.info(
            "Exiting function: %s, Execution time: %.4f seconds",
            func.__name__,
            time.time() - start_time,
        )

    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = _log_entry(args, kwargs)
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                _log_result(logger, result)
                return result
            except Exception as e:
                logger.exception("Exception occurred in function %s: %s", func.__name__, e)
                raise
            finally:
                _log_exit(logger, start_time)

        return async_wrapper

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = _log_entry(args, kwargs)
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            _log_result(logger, result)
            return result
        except Exception as e:
            logger.exception("Exception occurred in function %s: %s", func.__name__, e)
            raise
        finally:
            _log_exit(logger, start_time)

    return wrapper
