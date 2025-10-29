from flask import Blueprint, request, jsonify, send_file
import os
from config import UPLOAD_FOLDER, DATA_FOLDER, TEMP_FOLDER, RAW_DATA_PATH, MASTER_FILE_PATH

files_bp = Blueprint("files", __name__)

@files_bp.route("/reset", methods=["POST"])
def reset_files():
    for file in [RAW_DATA_PATH, MASTER_FILE_PATH]:
        if os.path.exists(file):
            os.remove(file)
    return jsonify({"status": "success", "message": "Raw and Master files deleted"})

@files_bp.route("/upload_raw", methods=["POST"])
def upload_raw():
    if "raw_data" not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400
    file = request.files["raw_data"]
    file.save(RAW_DATA_PATH)
    return jsonify({"status": "success", "saved_path": RAW_DATA_PATH})

@files_bp.route("/upload_master", methods=["POST"])
def upload_master():
    if "master_file" not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400
    file = request.files["master_file"]
    file.save(MASTER_FILE_PATH)
    return jsonify({"status": "success", "saved_path": MASTER_FILE_PATH})

@files_bp.route("/list_files", methods=["GET"])
def list_files():
    files = os.listdir(DATA_FOLDER)
    links = {f: f"/download/{f}" for f in files}
    return jsonify(links)

@files_bp.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    path = os.path.join(DATA_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return jsonify({"status": "error", "message": "File not found"}), 404
