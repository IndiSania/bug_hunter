from flask import Blueprint, current_app, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from pathlib import Path
from scanner.engine import scan_file, scan_project
import zipfile, tempfile, shutil, json, uuid, datetime

main = Blueprint("main", __name__)
history = []

def allowed(name):
    return name.lower().endswith((".py", ".zip"))

@main.route("/")
def index():
    return render_template("index.html", history=history[-8:][::-1])

@main.post("/scan")
def scan():
    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename:
        return jsonify({"error": "Pilih file Python atau ZIP project terlebih dahulu."}), 400
    if not allowed(uploaded.filename):
        return jsonify({"error": "Format hanya .py atau .zip."}), 400

    scan_id = uuid.uuid4().hex[:10]
    safe_name = secure_filename(uploaded.filename)
    temp = Path(current_app.config["UPLOAD_FOLDER"]) / f"{scan_id}_{safe_name}"
    uploaded.save(temp)

    try:
        if safe_name.lower().endswith(".zip"):
            with tempfile.TemporaryDirectory() as td:
                extract = Path(td)
                with zipfile.ZipFile(temp) as z:
                    members = [m for m in z.namelist() if not Path(m).is_absolute() and ".." not in Path(m).parts]
                    for m in members:
                        z.extract(m, extract)
                result = scan_project(extract)
        else:
            result = scan_file(temp)
    finally:
        temp.unlink(missing_ok=True)

    result["id"] = scan_id
    result["filename"] = safe_name
    result["created_at"] = datetime.datetime.now().strftime("%d %b %Y, %H:%M")
    history.append(result)
    history[:] = history[-20:]

    report = current_app.config["REPORT_FOLDER"] / f"{scan_id}.json"
    report.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    return jsonify(result)

@main.get("/report/<scan_id>")
def report(scan_id):
    path = current_app.config["REPORT_FOLDER"] / f"{scan_id}.json"
    if not path.exists():
        return jsonify({"error": "Report tidak ditemukan."}), 404
    return send_file(path, as_attachment=True, download_name=f"bughunter-{scan_id}.json")
