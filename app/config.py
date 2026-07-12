"""app/config.py — All config loaded from .env (local) or platform env vars (Render/cloud)"""
import os
from dotenv import load_dotenv

# Only load .env file if it actually exists on disk (local development).
# On Render/cloud, env vars are injected directly — load_dotenv is skipped.
_env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path, override=False, encoding="utf-8-sig")


class Config:
    SECRET_KEY           = os.getenv("SECRET_KEY", "dev-secret")
    SESSION_PERMANENT    = False
    IBM_API_KEY          = os.getenv("IBM_API_KEY", "")
    IBM_PROJECT_ID       = os.getenv("IBM_PROJECT_ID", "")
    IBM_WATSONX_URL      = os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    # granite-3-8b-instruct is WITHDRAWN (2026-03-31); default to granite-4-h-small
    WATSONX_MODEL_ID     = os.getenv("WATSONX_MODEL_ID", "ibm/granite-4-h-small")
    WATSONX_MAX_TOKENS   = int(os.getenv("WATSONX_MAX_TOKENS",   "900"))
    WATSONX_TEMPERATURE  = float(os.getenv("WATSONX_TEMPERATURE", "0.7"))
    WATSONX_TOP_P        = float(os.getenv("WATSONX_TOP_P",       "0.9"))
    WATSONX_REP_PENALTY  = float(os.getenv("WATSONX_REP_PENALTY", "1.1"))
    CACHE_TYPE           = os.getenv("CACHE_TYPE", "SimpleCache")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))
    APP_NAME    = "FutureMentor"
    APP_VERSION = "2.0.0"
    APP_TAGLINE = "Your AI Career Guide for a Better Tomorrow"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING        = True
    DEBUG          = True
    IBM_API_KEY    = "test-key"
    IBM_PROJECT_ID = "test-project"


config_map = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
    "default":     DevelopmentConfig,
}
