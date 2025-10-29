import os

# Get the directory containing the python server project
# (Assuming config.py is directly inside the python server folder)
PYTHON_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the JS server's upload folder relative to the python server
# Go up one level (..) to 'Term Fees Project', then down into 'js server', then 'uploads'
JS_UPLOADS_FOLDER = os.path.abspath(os.path.join(PYTHON_SERVER_DIR, "..", "js server", "uploads"))

# Use the JS uploads folder as the source for raw and master files
DATA_FOLDER = JS_UPLOADS_FOLDER # Point DATA_FOLDER to the JS uploads
UPLOAD_FOLDER = os.path.join(DATA_FOLDER, "uploads") # Keep this if needed, but likely unused now
TEMP_FOLDER = os.path.join(DATA_FOLDER, "temp") # Keep this if needed, but likely unused now

RAW_DATA_PATH = os.path.join(DATA_FOLDER, "raw_data.xlsx")
MASTER_FILE_PATH = os.path.join(DATA_FOLDER, "master_file.xlsx")

# Create the target DATA_FOLDER if it doesn't exist (important!)
os.makedirs(DATA_FOLDER, exist_ok=True)
# These might not be strictly necessary anymore if JS handles the temp uploads elsewhere,
# but it doesn't hurt to leave them for now.
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(TEMP_FOLDER, exist_ok=True)

print(f"--- Python Config ---")
print(f"Expecting data files in: {DATA_FOLDER}")
print(f"Raw data path: {RAW_DATA_PATH}")
print(f"Master file path: {MASTER_FILE_PATH}")
print(f"---------------------")