import os

# Get the directory of the current file
PYTHON_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))

# Use Render's environment variable for the persistent disk path,
# or fall back to a local 'data' folder for development.
DEFAULT_DATA_PATH = os.path.join(PYTHON_SERVER_DIR, "data")
DATA_FOLDER = os.environ.get('PYTHON_DATA_PATH', DEFAULT_DATA_PATH)

# Create the target DATA_FOLDER if it doesn't exist
os.makedirs(DATA_FOLDER, exist_ok=True)

# Define file paths
RAW_DATA_PATH = os.path.join(DATA_FOLDER, "raw_data.xlsx")
MASTER_FILE_PATH = os.path.join(DATA_FOLDER, "master_file.xlsx")

# These paths are likely unused now but are safe to keep
UPLOAD_FOLDER = os.path.join(DATA_FOLDER, "uploads")
TEMP_FOLDER = os.path.join(DATA_FOLDER, "temp")

print(f"--- Python Config ---")
print(f"Data folder is: {DATA_FOLDER}")
print(f"Raw data path: {RAW_DATA_PATH}")
print(f"Master file path: {MASTER_FILE_PATH}")
print(f"---------------------")
