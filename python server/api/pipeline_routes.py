from flask import Blueprint, request, jsonify, send_file
from pipeline.pp import run_pipeline_api
from config import RAW_DATA_PATH, MASTER_FILE_PATH, DATA_FOLDER
import os

pipeline_bp = Blueprint("pipeline", __name__)

MAPPED_FILE_PATH = os.path.join(DATA_FOLDER, "mapped.xlsx")

@pipeline_bp.route("/run_pipeline", methods=["POST"])
def run_pipeline():
    raw_path = RAW_DATA_PATH
    master_path = MASTER_FILE_PATH

    if "raw_data" in request.files:
        request.files["raw_data"].save(RAW_DATA_PATH)
        raw_path = RAW_DATA_PATH

    if "master_file" in request.files:
        request.files["master_file"].save(MASTER_FILE_PATH)
        master_path = MASTER_FILE_PATH

    if not os.path.exists(raw_path) or not os.path.exists(master_path):
        return jsonify({
            "status": "error",
            "message": "Missing input files. Upload via /upload_raw and /upload_master first."
        }), 400

    result = run_pipeline_api(raw_path, master_path)
    return jsonify(result)

@pipeline_bp.route("/download_mapped", methods=["GET"])
def download_mapped():
    if os.path.exists(MAPPED_FILE_PATH):
        return send_file(MAPPED_FILE_PATH, as_attachment=True)
    return jsonify({
        "status": "error",
        "message": "Mapped file not found. Run the pipeline first."
    }), 404
