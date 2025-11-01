import pandas as pd
import os
from openpyxl import load_workbook 

def run_pipeline_api(raw_data_file_path, master_file_path):
    """
    Cleans, maps, and merges student transaction data.
    This version is Flask-safe: takes file paths as args and returns a status dict.
    It now also appends all unmapped data to the end of the file.
    """
    try:
        print("--- Running Data Mapping Pipeline ---")

        if not os.path.exists(master_file_path):
            return {"status": "error", "message": f"Master file not found: {master_file_path}"}

        if not os.path.exists(raw_data_file_path):
            return {"status": "error", "message": f"Raw data file not found: {raw_data_file_path}"}

        output_filename = os.path.join(os.path.dirname(master_file_path), "mapped.xlsx")

        # 1️⃣ Read Master file
        master_df = pd.read_excel(master_file_path, engine='openpyxl')

        # 2️⃣ Read Raw data file robustly
        print("Reading raw data file with dynamic column handling...")
        raw_df_unparsed = pd.read_excel(
            raw_data_file_path, skiprows=8, skipfooter=4, header=None, engine='openpyxl'
        )

        clean_data_list = []
        unmapped_data_list = [] # To store all leftover rows
        
        # This variable will hold the header definition for all rows that follow
        current_header_map = {}

        for index, row in raw_df_unparsed.iterrows():
            row_values = [str(val).strip() for val in row.values]

            # --- NEW LOGIC TO FIND HEADERS ---
            if row_values[0] == 'Category Name':
                print(f"Header found at raw file row {index + 9}. Re-mapping column indices...")
                current_header_map = {} # Reset mapping
                
                # Try to find 'Enrollment No'
                try:
                    enroll_idx = row_values.index('Enrollment No')
                except ValueError:
                    # Try to find 'Enrollment/ACPC merit No'
                    try:
                        enroll_idx = row_values.index('Enrollment/ACPC merit No')
                        print("Found 'Enrollment/ACPC merit No' as Enrollment No")
                    except ValueError:
                        print("Warning: This header has no 'Enrollment No' column. Skipping.")
                        continue # Skip this header row
                
                current_header_map['Enrollment No'] = enroll_idx

                # Find other required columns
                required_cols = [
                    'Amount', 'Bank Reference No', 'Category Name',
                    'Status', 'Name of Student', 'Transaction Date'
                ]
                for col_name in required_cols:
                    try:
                         current_header_map[col_name] = row_values.index(col_name)
                    except ValueError:
                        print(f"Warning: Header missing required column: {col_name}")
                        pass # Column is missing from this header
                
                continue # Skip the header row itself from processing

            # --- NEW LOGIC TO SKIP EMPTY ROWS ---
            if all(val == 'None' or val == '' or val.isspace() or val == 'nan' for val in row_values):
                continue # Skip empty rows

            # --- NEW LOGIC TO PROCESS OR CATCH DATA ---
            # If we have found a valid header, process the row
            if current_header_map and 'Enrollment No' in current_header_map:
                try:
                    # Create the record from the current header map
                    record = {}
                    for col_name, idx in current_header_map.items():
                        if idx < len(row_values):
                            record[col_name] = row_values[idx]
                        else:
                            record[col_name] = None

                    enroll_no = record.get('Enrollment No', 'INVALID')
                    
                    # --- FIX: Handle scientific notation (E+11) ---
                    enroll_no_clean = enroll_no
                    try:
                        enroll_no_clean = str(int(float(enroll_no)))
                    except (ValueError, TypeError):
                        enroll_no_clean = str(enroll_no).strip()
                    # --- END FIX ---

                    if len(enroll_no_clean) > 5 and enroll_no_clean[0].isdigit():
                        record['Enrollment No'] = enroll_no_clean # Store the cleaned version
                        clean_data_list.append(record)
                    else:
                        # Has a header but invalid enroll_no, so it's leftover
                        unmapped_data_list.append(row_values)
                except Exception as e:
                    print(f"Error processing row: {e}. Row added to unmapped.")
                    unmapped_data_list.append(row_values)
            else:
                # No valid header was found for this row, so it's leftover
                unmapped_data_list.append(row_values)


        raw_df = pd.DataFrame(clean_data_list)
        if raw_df.empty:
            print("Warning: No valid data was parsed from the raw file.")
            # We can continue, to allow appending unmapped data

        print(f"Parsed {len(raw_df)} valid rows.")

        # 3️⃣ Clean and prep data
        if not raw_df.empty:
            raw_df.dropna(subset=['Enrollment No'], inplace=True)
            raw_df['Amount'] = pd.to_numeric(raw_df['Amount'], errors='coerce')
            raw_df.dropna(subset=['Amount'], inplace=True)
            raw_df['Enrollment No'] = raw_df['Enrollment No'].astype(str).str.strip()
            raw_df.drop_duplicates(subset=['Enrollment No'], keep='last', inplace=True)

        unnamed_col_name = master_df.columns[4]
        master_df['erno'] = master_df['erno'].astype(str).str.strip()


        # 4️⃣ Mapping dictionaries
        if not raw_df.empty:
            amount_map = raw_df.set_index('Enrollment No')['Amount'].to_dict()
            ref_map = raw_df.set_index('Enrollment No')['Bank Reference No'].to_dict() if 'Bank Reference No' in raw_df.columns else {}
            type_map = raw_df.set_index('Enrollment No')['Category Name'].to_dict() if 'Category Name' in raw_df.columns else {}
            status_map = raw_df.set_index('Enrollment No')['Status'].to_dict() if 'Status' in raw_df.columns else {}
            date_map = raw_df.set_index('Enrollment No')['Transaction Date'].to_dict() if 'Transaction Date' in raw_df.columns else {}
        else:
            amount_map, ref_map, type_map, status_map, date_map = {}, {}, {}, {}, {}

        # 5️⃣ Map data to master
        master_df['AMOUNT'] = master_df['erno'].map(amount_map)
        master_df['epaymerchantorderno'] = master_df['erno'].map(ref_map)
        master_df['TYPE'] = master_df['erno'].map(type_map)
        master_df['FEES'] = master_df['erno'].map(status_map)
        master_df['modifydate'] = master_df['erno'].map(date_map)
        master_df['ERNO'] = master_df['erno']
        master_df['NAME'] = master_df['name']

        # Fill missing values
        master_df['AMOUNT'] = master_df['AMOUNT'].fillna(0)
        master_df['epaymerchantorderno'] = master_df['epaymerchantorderno'].fillna('')
        master_df['TYPE'] = master_df['TYPE'].fillna('')
        master_df['FEES'] = master_df['FEES'].fillna('Not Paid')
        master_df['modifydate'] = master_df['modifydate'].fillna('')

        # 6️⃣ Add new students
        if not raw_df.empty:
            master_ernos = set(master_df['erno'])
            raw_ernos = set(raw_df['Enrollment No'])
            new_student_ernos = raw_ernos - master_ernos

            if new_student_ernos:
                print(f"Found {len(new_student_ernos)} new students.")
                # Filter raw_df for new students
                new_students_df = raw_df[raw_df['Enrollment No'].isin(new_student_ernos)].copy()
                
                # --- THIS IS THE BUG FIX ---
                # Create a new DataFrame for these new students
                new_rows_df = pd.DataFrame()
                
                # Use .values to safely extract data
                new_rows_df['erno'] = new_students_df['Enrollment No'].values
                new_rows_df['name'] = new_students_df['Name of Student'].values if 'Name of Student' in new_students_df.columns else ''
                new_rows_df['AMOUNT'] = new_students_df['Amount'].values if 'Amount' in new_students_df.columns else 0
                new_rows_df['modifydate'] = new_students_df['Transaction Date'].values if 'Transaction Date' in new_students_df.columns else ''
                new_rows_df['epaymerchantorderno'] = new_students_df['Bank Reference No'].values if 'Bank Reference No' in new_students_df.columns else ''
                new_rows_df['ERNO'] = new_students_df['Enrollment No'].values
                new_rows_df['NAME'] = new_students_df['Name of Student'].values if 'Name of Student' in new_students_df.columns else ''
                new_rows_df['TYPE'] = new_students_df['Category Name'].values if 'Category Name' in new_students_df.columns else ''
                new_rows_df['FEES'] = new_students_df['Status'].values if 'Status' in new_students_df.columns else ''
                # --- END OF BUG FIX ---

                new_rows_df['sem'] = 'NEW'
                new_rows_df['br_code'] = 'NEW'
                
                # Add the unnamed column if it exists in master_df
                if unnamed_col_name in master_df.columns:
                    new_rows_df[unnamed_col_name] = ''
                
                # Ensure all columns from master_df are present
                for col in master_df.columns:
                    if col not in new_rows_df.columns:
                        new_rows_df[col] = pd.NA
                
                # Reorder and select only columns that are in master_df
                new_rows_df = new_rows_df[master_df.columns]
                
                new_rows_df.fillna({
                    'AMOUNT': 0, 'epaymerchantorderno': '', 'TYPE': '',
                    'FEES': 'Paid', 'modifydate': ''
                }, inplace=True)
                
                master_df = pd.concat([master_df, new_rows_df], ignore_index=True)

        # 7️⃣ Save final file
        master_df.to_excel(output_filename, index=False)
        print(f"✅ Main mapping complete. Saved to {output_filename}")

        # --- NEW LOGIC: APPEND UNMAPPED DATA ---
        if unmapped_data_list:
            print(f"Appending {len(unmapped_data_list)} unmapped rows to the file...")
            try:
                wb = load_workbook(output_filename)
                ws = wb.active
                
                # Add a spacer and a title
                ws.append([]) # Blank row
                ws.append(["--- Unmapped Raw Data (Skipped by Pipeline) ---"])
                
                # Add a generic header
                max_cols = max(len(row) for row in unmapped_data_list)
                generic_header = [f"Raw Column {i+1}" for i in range(max_cols)]
                ws.append(generic_header)

                # Append each unmapped row
                for row in unmapped_data_list:
                    # Ensure row has full width to avoid data shifting
                    full_row = row + [None] * (max_cols - len(row))
                    ws.append(full_row)
                
                wb.save(output_filename)
                print("✅ Unmapped data appended successfully.")
            except Exception as e:
                print(f"⚠️ Warning: Could not append unmapped data to Excel file: {e}")
        # --- END NEW LOGIC ---

        return {
            "status": "success",
            "message": f"Mapping complete. {len(unmapped_data_list)} unmapped rows were appended.",
            "output_file": output_filename,
            "records_processed": len(master_df)
        }

    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {e}"}