import pandas as pd
import os

def check_excel(excel_path):
    print(f"\nChecking Excel file: {excel_path}")
    if not os.path.exists(excel_path):
        print(f"Error: File not found at {excel_path}")
        return
        
    print(f"File size: {os.path.getsize(excel_path)} bytes")
    
    try:
        # Read Excel file
        excel_file = pd.ExcelFile(excel_path)
        
        print("\nSheets in Excel file:")
        for sheet in excel_file.sheet_names:
            print(f"\n=== Sheet: {sheet} ===")
            df = pd.read_excel(excel_file, sheet)
            print(f"Columns: {list(df.columns)}")
            print(f"Row count: {len(df)}")
            print("\nFirst few rows:")
            print(df.head().to_string())
            print("\n" + "="*50)
            
    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")

if __name__ == "__main__":
    # Try both possible filenames
    files_to_check = ['hardware.xlsx', 'hardware_data.xlsx']
    
    for filename in files_to_check:
        excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        check_excel(excel_path)
