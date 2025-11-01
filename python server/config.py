import os

# Get the username from the environment, which PythonAnywhere sets
USER = os.environ.get('USER', 'defaultuser')
PYTHON_SERVER_DIR = f'/home/{USER}/clgproject/python server'

# Define the data folder *within* your project structure
DATA_FOLDER = os.path.join(PYTHON_SERVER_DIR, "data")

# Create the target DATA_FOLDER if it doesn't exist
os.makedirs(DATA_FOLDER, exist_ok=True)

# Define file paths
RAW_DATA_PATH = os.path.join(DATA_FOLDER, "raw_data.xlsx")
MASTER_FILE_PATH = os.path.join(DATA_FOLDER, "master_file.xlsx")

print(f"--- Python Config ---")
print(f"Data folder is: {DATA_FOLDER}")
print(f"Raw data path: {RAW_DATA_PATH}")
print(f"Master file path: {MASTER_FILE_PATH}")
print(f"---------------------")
