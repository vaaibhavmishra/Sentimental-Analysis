import os


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "sentivista-dev-key")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB upload limit
    MODEL_NAME = os.environ.get(
        "MODEL_NAME", "nlptown/bert-base-multilingual-uncased-sentiment"
    )
    MAX_TEXT_LENGTH = 5000


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
