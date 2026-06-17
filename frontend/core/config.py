from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Process-wide configuration sourced from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    backend_endpoint: str = Field(default="http://backend:8000")
    frontend_port: int = Field(default=8080)
    frontend_log_level: str = Field(default="INFO")
    frontend_log_file: str = Field(default="/app/logs/frontend.log")
    frontend_logger_name: str = Field(default="linguai.frontend")
    http_connect_timeout_s: float = Field(default=5.0)
    http_read_timeout_s: float = Field(default=15.0)
    # Signing key for NiceGUI's app.storage.user cookie. The hardcoded default
    # below is for dev only; production deployments MUST override via env so
    # the cookie cannot be forged. Logged as a warning at startup when the
    # default is in use.
    frontend_storage_secret: str = Field(default="linguai-frontend-dev-secret")
