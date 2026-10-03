from flask import Flask
from pathlib import Path

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "bughunter-development-key"
    app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

    root = Path(app.root_path).parent
    app.config["UPLOAD_FOLDER"] = root / "uploads"
    app.config["REPORT_FOLDER"] = root / "reports"

    app.config["UPLOAD_FOLDER"].mkdir(exist_ok=True)
    app.config["REPORT_FOLDER"].mkdir(exist_ok=True)

    from app.routes import main
    app.register_blueprint(main)

    return app
