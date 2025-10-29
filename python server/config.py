import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data")
UPLOAD_FOLDER = os.path.join(DATA_FOLDER, "uploads")
TEMP_FOLDER = os.path.join(DATA_FOLDER, "temp")

RAW_DATA_PATH = os.path.join(DATA_FOLDER, "raw_data.xlsx")
MASTER_FILE_PATH = os.path.join(DATA_FOLDER, "master_file.xlsx")

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)
