from core.config import AppConfig


def test_app_config_reads_env(monkeypatch):
    monkeypatch.setenv("BACKEND_ENDPOINT", "http://example.test:9000")
    monkeypatch.setenv("FRONTEND_LOG_LEVEL", "DEBUG")
    cfg = AppConfig()
    assert cfg.backend_endpoint == "http://example.test:9000"
    assert cfg.frontend_log_level == "DEBUG"


def test_app_config_defaults(monkeypatch):
    monkeypatch.delenv("BACKEND_ENDPOINT", raising=False)
    monkeypatch.delenv("FRONTEND_LOG_LEVEL", raising=False)
    cfg = AppConfig()
    assert cfg.backend_endpoint == "http://backend:8000"
    assert cfg.frontend_log_level == "INFO"
