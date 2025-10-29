import pandas as pd
import os

def run_pipeline_api(raw_data_file_path, master_file_path):
    """
    Cleans, maps, and merges student transaction data.
    This version is Flask-safe: takes file paths as args and returns a status dict.
    """
    try:
        print("--- Running Data Mapping Pipeline ---")

        if not os.path.exists(master_file_path):
            return {"status": "error", "message": f"Master file not found: {master_file_path}"}

        if not os.path.exists(raw_data_file_path):
            return {"status": "error", "message": f"Raw data file not found: {raw_data_file_path}"}

        output_filename = os.path.join(os.path.dirname(master_file_path), "mapped.xlsx")

        # 1️⃣ Read Master file
        master_df = pd.read_excel(master_file_path)

        # 2️⃣ Read Raw data file robustly
        print("Reading raw data file with dynamic column handling...")
        raw_df_unparsed = pd.read_excel(
            raw_data_file_path, skiprows=8, skipfooter=4, header=None, engine='openpyxl'
        )

        clean_data_list = []
        col_indices = {}
        required_cols = [
            'Enrollment No', 'Amount', 'Bank Reference No',
            'Category Name', 'Status', 'Name of Student', 'Transaction Date'
        ]

        for index, row in raw_df_unparsed.iterrows():
            row_values = [str(val).strip() for val in row.values]

            if row_values[0] == 'Category Name':
                print(f"Header found at raw file row {index + 9}. Re-mapping column indices...")
                col_indices = {}
                for col_name in required_cols:
                    try:
                        col_indices[col_name] = row_values.index(col_name)
                    except ValueError:
                        pass
                continue

            if not col_indices or 'Enrollment No' not in col_indices:
                continue

            try:
                record = {col_name: row_values[idx] for col_name, idx in col_indices.items()}
                enroll_no = record.get('Enrollment No', 'INVALID')
                if len(enroll_no) > 5 and enroll_no[0].isdigit():
                    clean_data_list.append(record)
            except Exception as e:
                print(f"Skipping malformed row {index + 9}: {e}")

        raw_df = pd.DataFrame(clean_data_list)
        if raw_df.empty:
            return {"status": "error", "message": "No valid data parsed from raw file"}

        print(f"Parsed {len(raw_df)} valid rows.")

        # 3️⃣ Clean and prep data
        raw_df.dropna(subset=['Enrollment No'], inplace=True)
        raw_df['Amount'] = pd.to_numeric(raw_df['Amount'], errors='coerce')
        raw_df.dropna(subset=['Amount'], inplace=True)

        unnamed_col_name = master_df.columns[4]
        master_df['erno'] = master_df['erno'].astype(str).str.strip()
        raw_df['Enrollment No'] = raw_df['Enrollment No'].astype(str).str.strip()
        raw_df.drop_duplicates(subset=['Enrollment No'], keep='last', inplace=True)

        # 4️⃣ Mapping dictionaries
        amount_map = raw_df.set_index('Enrollment No')['Amount'].to_dict()
        ref_map = raw_df.set_index('Enrollment No')['Bank Reference No'].to_dict()
        type_map = raw_df.set_index('Enrollment No')['Category Name'].to_dict()
        status_map = raw_df.set_index('Enrollment No')['Status'].to_dict()
        date_map = raw_df.set_index('Enrollment No')['Transaction Date'].to_dict()

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
        master_ernos = set(master_df['erno'])
        raw_ernos = set(raw_df['Enrollment No'])
        new_student_ernos = raw_ernos - master_ernos

        if new_student_ernos:
            print(f"Found {len(new_student_ernos)} new students.")
            new_students_df = raw_df[raw_df['Enrollment No'].isin(new_student_ernos)].copy()
            new_rows_df = pd.DataFrame(columns=master_df.columns)
            new_rows_df['erno'] = new_students_df['Enrollment No'].values
            new_rows_df['name'] = new_students_df['Name of Student'].values
            new_rows_df['AMOUNT'] = new_students_df['Amount'].values
            new_rows_df['modifydate'] = new_students_df['Transaction Date'].values
            new_rows_df['epaymerchantorderno'] = new_students_df['Bank Reference No'].values
            new_rows_df['ERNO'] = new_students_df['Enrollment No'].values
            new_rows_df['NAME'] = new_students_df['Name of Student'].values
            new_rows_df['TYPE'] = new_students_df['Category Name'].values
            new_rows_df['FEES'] = new_students_df['Status'].values
            new_rows_df['sem'] = 'NEW'
            new_rows_df['br_code'] = 'NEW'
            new_rows_df[unnamed_col_name] = ''
            new_rows_df.fillna({
                'AMOUNT': 0, 'epaymerchantorderno': '', 'TYPE': '',
                'FEES': 'Paid', 'modifydate': ''
            }, inplace=True)
            new_rows_df = new_rows_df[master_df.columns]
            master_df = pd.concat([master_df, new_rows_df], ignore_index=True)

        # 7️⃣ Save final file
        master_df.to_excel(output_filename, index=False)
        print(f"✅ Mapping complete. Saved to {output_filename}")

        return {
            "status": "success",
            "message": "Mapping complete, including new students.",
            "output_file": output_filename,
            "records_processed": len(master_df)
        }

    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {e}"}
