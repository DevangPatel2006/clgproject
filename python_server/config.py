import os
import tempfile

# Use a temporary directory for file storage in production
# This will be isolated to each Python server instance
TEMP_DIR = tempfile.gettempdir()
DATA_FOLDER = os.path.join(TEMP_DIR, "student_data_processing")

# Create the data folder if it doesn't exist
os.makedirs(DATA_FOLDER, exist_ok=True)

RAW_DATA_PATH = os.path.join(DATA_FOLDER, "raw_data.xlsx")
MASTER_FILE_PATH = os.path.join(DATA_FOLDER, "master_file.xlsx")
MAPPED_FILE_PATH = os.path.join(DATA_FOLDER, "mapped.xlsx")

# Maximum file size (e.g., 16MB)
MAX_FILE_SIZE = 16 * 1024 * 1024

print(f"--- Python Config (Production Ready) ---")
print(f"Data folder: {DATA_FOLDER}")
print(f"Raw data path: {RAW_DATA_PATH}")
print(f"Master file path: {MASTER_FILE_PATH}")
print(f"Mapped file path: {MAPPED_FILE_PATH}")
print(f"----------------------------------------")
