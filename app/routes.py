"""routes.py — Flask routes (v2)"""

import os
import uuid
from flask import (
    Blueprint, render_template, request,
    current_app, send_file, flash, redirect, url_for, jsonify
)
from werkzeug.utils import secure_filename
from .generator import generate_tests

bp = Blueprint("main", __name__)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "py"


@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@bp.route("/generate", methods=["POST"])
def generate():
    if "python_file" not in request.files:
        flash("No file selected.", "error")
        return redirect(url_for("main.index"))

    f = request.files["python_file"]
    if not f or f.filename == "" or not allowed_file(f.filename):
        flash("Only .py files are accepted.", "error")
        return redirect(url_for("main.index"))

    filename  = secure_filename(f.filename)
    uid       = uuid.uuid4().hex[:8]
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], f"{uid}_{filename}")
    f.save(save_path)

    with open(save_path, "r", encoding="utf-8") as fh:
        source_code = fh.read()

    module_name  = filename[:-3]
    template_dir = os.path.join(current_app.root_path, "templates")

    try:
        test_code, conftest_code, functions, stats = generate_tests(
            source_code, module_name, template_dir
        )
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("main.index"))

    # Save both generated files
    test_filename     = f"test_{module_name}_{uid}.py"
    conftest_filename = f"conftest_{module_name}_{uid}.py"
    gen_dir           = current_app.config["GENERATED_FOLDER"]

    with open(os.path.join(gen_dir, test_filename), "w", encoding="utf-8") as fh:
        fh.write(test_code)
    with open(os.path.join(gen_dir, conftest_filename), "w", encoding="utf-8") as fh:
        fh.write(conftest_code)

    return render_template(
        "result.html",
        module_name       = module_name,
        source_code       = source_code,
        test_code         = test_code,
        conftest_code     = conftest_code,
        functions         = functions,
        stats             = stats,
        test_filename     = test_filename,
        conftest_filename = conftest_filename,
        original_filename = filename,
    )


@bp.route("/download/<filename>")
def download(filename: str):
    safe = secure_filename(filename)
    path = os.path.join(current_app.config["GENERATED_FOLDER"], safe)
    if not os.path.exists(path):
        flash("File not found.", "error")
        return redirect(url_for("main.index"))
    return send_file(path, as_attachment=True, download_name=safe)


@bp.route("/api/generate", methods=["POST"])
def api_generate():
    payload = request.get_json(silent=True)
    if not payload or "source" not in payload:
        return jsonify({"error": "Send JSON with 'source' key"}), 400

    source_code  = payload["source"]
    module_name  = payload.get("module", "my_module")
    template_dir = os.path.join(current_app.root_path, "templates")

    try:
        test_code, conftest_code, _, stats = generate_tests(
            source_code, module_name, template_dir
        )
        return jsonify({"test_code": test_code, "conftest_code": conftest_code, "stats": stats})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 422