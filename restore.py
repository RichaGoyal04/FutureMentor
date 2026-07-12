"""
restore.py — FutureMentor single-file project regenerator
═══════════════════════════════════════════════════════════
Run this if any project files get deleted or corrupted.
It recreates ALL source files from the embedded content below.

Usage:
    python restore.py           # preview only (dry run)
    python restore.py --write   # actually write all files
    python restore.py --write --force   # overwrite existing files too
"""
import os, sys, textwrap

WRITE  = "--write" in sys.argv
FORCE  = "--force" in sys.argv
ROOT   = os.path.dirname(os.path.abspath(__file__))
W      = "\033[93m"; G = "\033[92m"; R = "\033[91m"; RST = "\033[0m"

def save(rel_path: str, content: str):
    full = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    exists = os.path.exists(full)
    if exists and not FORCE:
        print(f"{W}  ⏭  SKIP  {rel_path}  (exists — use --force to overwrite){RST}")
        return
    if WRITE:
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"{G}  ✅ WROTE {rel_path}{RST}")
    else:
        tag = "OVERWRITE" if exists else "CREATE"
        print(f"  🔍 {tag:9}  {rel_path}")


# ══════════════════════════════════════════════════════════════════
# FILE CONTENTS
# ══════════════════════════════════════════════════════════════════

FILES: dict[str, str] = {}

# ── requirements.txt ──────────────────────────────────────────────
FILES["requirements.txt"] = textwrap.dedent("""\
    flask>=3.0.0
    flask-caching>=2.1.0
    flask-cors>=4.0.0
    python-dotenv>=1.0.0
    requests>=2.31.0
    gunicorn>=21.2.0
""")

# ── .env.example ──────────────────────────────────────────────────
FILES[".env.example"] = textwrap.dedent("""\
    # ── IBM watsonx.ai credentials ──────────────────────────────────
    # Get API key:    https://cloud.ibm.com/iam/apikeys
    # Get Project ID: https://dataplatform.cloud.ibm.com/projects
    #                 (Open project → Manage → General → Project ID)

    IBM_API_KEY=your_ibm_api_key_here
    IBM_PROJECT_ID=your_project_id_here

    # ── Region / Model ───────────────────────────────────────────────
    # Recommended: us-south (granite-3-8b-instruct available here)
    # Options: us-south | eu-de  (eu-gb and au-syd lack this model)
    IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
    WATSONX_MODEL_ID=ibm/granite-3-8b-instruct

    # ── Optional tuning ──────────────────────────────────────────────
    WATSONX_MAX_TOKENS=900
    WATSONX_TEMPERATURE=0.7
    WATSONX_TOP_P=0.9
    WATSONX_REP_PENALTY=1.1

    # ── Flask ─────────────────────────────────────────────────────────
    SECRET_KEY=change-this-to-a-random-long-string
    FLASK_ENV=development
    PORT=5000
""")

# ── run.py ────────────────────────────────────────────────────────
FILES["run.py"] = textwrap.dedent('''\
    """run.py — FutureMentor development server entry point"""
    import os
    from app import create_app

    app = create_app(os.getenv("FLASK_ENV", "development"))

    if __name__ == "__main__":
        port = int(os.getenv("PORT", 5000))
        print(f"\\n{\'=\'*60}")
        print("  🎓 FutureMentor — AI Career Guide for Informal Workers")
        print(f"{\'=\'*60}")
        print(f"  ▶  http://localhost:{port}")
        print(f"  🤖  Model: {os.getenv(\'WATSONX_MODEL_ID\',\'ibm/granite-3-8b-instruct\')}")
        print(f"{\'=\'*60}\\n")
        app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", True))
''')

# ── app/__init__.py ───────────────────────────────────────────────
FILES["app/__init__.py"] = textwrap.dedent('''\
    """app/__init__.py — Flask application factory"""
    import logging, os
    from flask import Flask
    from flask_caching import Cache
    from flask_cors import CORS
    from app.config import config_map

    cache = Cache()

    def create_app(env=None):
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
            return dict(app_name=app.config["APP_NAME"],
                        app_tagline=app.config["APP_TAGLINE"])

        @app.get("/health")
        def health():
            return {"status": "ok", "app": app.config["APP_NAME"]}

        return app
''')

# ── app/config.py ─────────────────────────────────────────────────
FILES["app/config.py"] = textwrap.dedent('''\
    """app/config.py — All config loaded from .env"""
    import os
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

    class Config:
        SECRET_KEY           = os.getenv("SECRET_KEY", "dev-secret")
        SESSION_PERMANENT    = False
        IBM_API_KEY          = os.getenv("IBM_API_KEY", "")
        IBM_PROJECT_ID       = os.getenv("IBM_PROJECT_ID", "")
        IBM_WATSONX_URL      = os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        WATSONX_MODEL_ID     = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")
        WATSONX_MAX_TOKENS   = int(os.getenv("WATSONX_MAX_TOKENS", "900"))
        WATSONX_TEMPERATURE  = float(os.getenv("WATSONX_TEMPERATURE", "0.7"))
        WATSONX_TOP_P        = float(os.getenv("WATSONX_TOP_P", "0.9"))
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
        TESTING = True; DEBUG = True
        IBM_API_KEY = "test-key"; IBM_PROJECT_ID = "test-project"

    config_map = {
        "development": DevelopmentConfig,
        "production":  ProductionConfig,
        "testing":     TestingConfig,
        "default":     DevelopmentConfig,
    }
''')

# ── app/blueprints/__init__.py ────────────────────────────────────
FILES["app/blueprints/__init__.py"] = ""

# ── app/utils/__init__.py ─────────────────────────────────────────
FILES["app/utils/__init__.py"] = ""


def main():
    mode = "WRITE" if WRITE else "DRY RUN"
    force = " (+force overwrite)" if FORCE else ""
    print(f"\n{'='*60}")
    print(f"  🔄  FutureMentor — File Restore  [{mode}{force}]")
    print(f"{'='*60}\n")

    for rel, content in FILES.items():
        save(rel, content)

    print(f"\n{'='*60}")
    if WRITE:
        print(f"{G}  ✅  Restore complete!{RST}")
        print(f"  ▶  Run:  python run.py")
    else:
        print(f"{W}  ℹ️   DRY RUN — no files written.{RST}")
        print(f"  To actually write:  python restore.py --write")
        print(f"  To overwrite too:   python restore.py --write --force")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
