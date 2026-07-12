"""app/__init__.py — Flask application factory"""
import logging, os
from flask import Flask
from flask_caching import Cache
from flask_cors import CORS
from app.config import config_map

cache = Cache()


def create_app(env: str | None = None) -> Flask:
    env = env or os.getenv("FLASK_ENV", "development")
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_map.get(env, config_map["default"]))
    cache.init_app(app)
    CORS(app, origins="*")
    logging.basicConfig(
        level=logging.DEBUG if app.config.get("DEBUG") else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
    from app.blueprints.main    import main_bp
    from app.blueprints.mentor  import mentor_bp
    from app.blueprints.jobs    import jobs_bp
    from app.blueprints.skills  import skills_bp
    from app.blueprints.schemes import schemes_bp
    from app.blueprints.career  import career_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(mentor_bp,  url_prefix="/mentor")
    app.register_blueprint(jobs_bp,    url_prefix="/jobs")
    app.register_blueprint(skills_bp,  url_prefix="/skills")
    app.register_blueprint(schemes_bp, url_prefix="/schemes")
    app.register_blueprint(career_bp,  url_prefix="/career")

    @app.context_processor
    def _g():
        return dict(app_name=app.config["APP_NAME"], app_tagline=app.config["APP_TAGLINE"])

    @app.get("/health")
    def health():
        return {"status": "ok", "app": app.config["APP_NAME"]}

    return app
