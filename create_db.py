import pandas as pd
import sqlite3
import os

def create_and_load_database(excel_path, db_path='hardware.db'):
    print(f"Reading Excel file from: {excel_path}")
    print(f"Creating database at: {db_path}")
    
    try:
        # Create/connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read Excel file
        excel_file = pd.ExcelFile(excel_path)
        
        # Process each sheet
        for sheet_name in excel_file.sheet_names:
            print(f"\nProcessing sheet: {sheet_name}")
            df = pd.read_excel(excel_file, sheet_name)
            
            # Clean column names (remove spaces, special chars)
            df.columns = [col.strip().replace(' ', '_') for col in df.columns]
            
            # Create table name from sheet name
            table_name = ''.join(c if c.isalnum() else '_' for c in sheet_name)
            
            # Print schema information
            print(f"Creating table '{table_name}' with columns:")
            for col in df.columns:
                print(f"  - {col}")
            
            # Save to database
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            
            # Print sample data
            print("\nSample data (first 2 rows):")
            print(df.head(2))
            
            # Print row count
            print(f"\nTotal rows in {table_name}: {len(df)}")
        
        # Create backup of database
        backup_path = f"{db_path}.backup"
        with sqlite3.connect(backup_path) as backup:
            conn.backup(backup)
        print(f"\nCreated backup at: {backup_path}")
        
        conn.close()
        print("\nDatabase creation completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    excel_path = r"C:\Users\Admin-Frankie\Desktop\hardware.xlsx"
    create_and_load_database(excel_path)
