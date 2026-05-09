"""
app/__init__.py — Flask application factory
"""

import os
from flask import Flask


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="../static",
    )
    app.config["SECRET_KEY"] = "ast-test-gen-dev-key-2024"
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB cap

    # Ensure upload / output dirs exist
    base = os.path.dirname(os.path.dirname(__file__))
    app.config["UPLOAD_FOLDER"] = os.path.join(base, "uploads")
    app.config["GENERATED_FOLDER"] = os.path.join(base, "generated")

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["GENERATED_FOLDER"], exist_ok=True)

    from .routes import bp
    app.register_blueprint(bp)

    return app