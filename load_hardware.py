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

if __name__ == "__main__":
    # Your Excel file path
    excel_path = r"C:\Users\Admin-Frankie\Desktop\hardware.xlsx"
    
    print("Starting data load process...")
    success = load_excel_to_db(excel_path)
    
    if success:
        print("\nYou can now use the database to query your hardware data!")
        print("The database file 'excel_data.db' has been created in the current directory.")
