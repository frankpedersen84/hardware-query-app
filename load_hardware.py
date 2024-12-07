import pandas as pd
import sqlite3
from pathlib import Path

def load_excel_to_db(excel_path, db_path='excel_data.db'):
    """
    Load the hardware Excel file into SQLite database
    """
    try:
        # Read all sheets from Excel
        print(f"Reading Excel file: {excel_path}")
        excel_file = pd.ExcelFile(excel_path)
        
        # Create SQLite connection
        print(f"Creating/connecting to database: {db_path}")
        conn = sqlite3.connect(db_path)
        
        # Load each sheet into the database
        for sheet_name in excel_file.sheet_names:
            print(f"\nProcessing sheet: {sheet_name}")
            df = pd.read_excel(excel_file, sheet_name)
            
            # Clean the table name (remove spaces and special characters)
            table_name = ''.join(c if c.isalnum() else '_' for c in sheet_name)
            
            # Save to database
            print(f"Saving {len(df)} rows to table '{table_name}'")
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"Successfully saved sheet '{sheet_name}'")
            
            # Show sample of data
            print("\nFirst few rows of data:")
            print(df.head())
            print("\nColumns:", list(df.columns))
            
        conn.close()
        print("\nSuccessfully loaded all data into the database!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def generate_sample_excel():
    import pandas as pd

    # Sample hardware data
    data = {
        'name': ['Camera 1', 'Camera 2', 'Camera 3', 'DVR System', 'NVR System'],
        'ip_address': ['192.168.1.100', '192.168.1.101', '192.168.1.102', '192.168.1.200', '192.168.1.201'],
        'shortcut': ['CAM1', 'CAM2', 'CAM3', 'DVR1', 'NVR1'],
        'firmware_version': ['v2.1.0', 'v2.1.0', 'v2.0.9', 'v3.2.1', 'v4.0.0'],
        'unit': ['Main Building', 'Warehouse', 'Parking Lot', 'Security Room', 'IT Room']
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Save to Excel file
    df.to_excel('hardware_data.xlsx', index=False)
    print("Created hardware_data.xlsx with sample data")

if __name__ == "__main__":
    # Your Excel file path
    excel_path = r"C:\Users\Admin-Frankie\Desktop\hardware.xlsx"
    
    print("Starting data load process...")
    success = load_excel_to_db(excel_path)
    
    if success:
        print("\nYou can now use the database to query your hardware data!")
        print("The database file 'excel_data.db' has been created in the current directory.")
        
    generate_sample_excel()
