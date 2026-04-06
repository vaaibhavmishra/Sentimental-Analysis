import os
import logging

from flask import Flask

from config import config_map


def create_app():
    """Flask application factory."""
    env = os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_map.get(env, config_map["development"]))

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.analysis import analysis_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp)

    app.logger.info(f"Sentivista started in {env} mode")
    return app
