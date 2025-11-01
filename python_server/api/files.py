from flask import Blueprint, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
from config import DATA_FOLDER, RAW_DATA_PATH, MASTER_FILE_PATH, MAPPED_FILE_PATH, MAX_FILE_SIZE

files_bp = Blueprint("files", __name__)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@files_bp.route("/reset", methods=["POST"])
def reset_files():
    """Delete raw and master files"""
    deleted_files = []
    for file_path in [RAW_DATA_PATH, MASTER_FILE_PATH]:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                deleted_files.append(os.path.basename(file_path))
            except Exception as e:
                return jsonify({
                    "status": "error", 
                    "message": f"Failed to delete {os.path.basename(file_path)}: {str(e)}"
                }), 500
    
    return jsonify({
        "status": "success", 
        "message": "Files deleted successfully",
        "deleted_files": deleted_files
    })

@files_bp.route("/upload_raw", methods=["POST"])
def upload_raw():
    """Receive raw data file from JS server"""
    if "raw_data" not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400
    
    file = request.files["raw_data"]
    
    if file.filename == '':
        return jsonify({"status": "error", "message": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            "status": "error", 
            "message": "Invalid file type. Only .xlsx and .xls files are allowed"
        }), 400
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({
            "status": "error", 
            "message": f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024)}MB"
        }), 400
    
    try:
        file.save(RAW_DATA_PATH)
        return jsonify({
            "status": "success", 
            "message": "Raw data file uploaded successfully",
            "saved_path": RAW_DATA_PATH,
            "file_size": file_size
        })
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Failed to save file: {str(e)}"
        }), 500

@files_bp.route("/upload_master", methods=["POST"])
def upload_master():
    """Receive master file from JS server"""
    if "master_file" not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400
    
    file = request.files["master_file"]
    
    if file.filename == '':
        return jsonify({"status": "error", "message": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            "status": "error", 
            "message": "Invalid file type. Only .xlsx and .xls files are allowed"
        }), 400
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({
            "status": "error", 
            "message": f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024)}MB"
        }), 400
    
    try:
        file.save(MASTER_FILE_PATH)
        return jsonify({
            "status": "success", 
            "message": "Master file uploaded successfully",
            "saved_path": MASTER_FILE_PATH,
            "file_size": file_size
        })
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Failed to save file: {str(e)}"
        }), 500

@files_bp.route("/list_files", methods=["GET"])
def list_files():
    """List all files in data folder"""
    try:
        files = os.listdir(DATA_FOLDER)
        file_info = {}
        for f in files:
            file_path = os.path.join(DATA_FOLDER, f)
            if os.path.isfile(file_path):
                file_info[f] = {
                    "download_url": f"/download/{f}",
                    "size": os.path.getsize(file_path)
                }
        return jsonify(file_info)
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Failed to list files: {str(e)}"
        }), 500

@files_bp.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    """Download a specific file"""
    # Secure the filename to prevent directory traversal attacks
    filename = secure_filename(filename)
    path = os.path.join(DATA_FOLDER, filename)
    
    if not os.path.exists(path):
        return jsonify({"status": "error", "message": "File not found"}), 404
    
    try:
        return send_file(path, as_attachment=True)
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Failed to send file: {str(e)}"
        }), 500