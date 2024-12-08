import pandas as pd
import sqlite3
import os

def create_and_load_database(excel_path, db_path='hardware.db'):
    print(f"\n=== Database Creation Process ===")
    print(f"Reading Excel file from: {excel_path}")
    print(f"Creating database at: {db_path}")
    
    try:
        # Create/connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read Excel file
        excel_file = pd.ExcelFile(excel_path)
        print(f"\nAvailable sheets in Excel:")
        for sheet in excel_file.sheet_names:
            print(f"  - {sheet}")
        
        # Process each sheet
        for sheet_name in excel_file.sheet_names:
            print(f"\nProcessing sheet: {sheet_name}")
            df = pd.read_excel(excel_file, sheet_name)
            
            # Clean column names (remove spaces, special chars)
            df.columns = [col.strip().lower().replace(' ', '_').replace('-', '_') for col in df.columns]
            
            # Create table name from sheet name (clean it up)
            table_name = sheet_name.strip().lower().replace(' ', '_').replace('-', '_')
            
            # Print schema information
            print(f"Creating table '{table_name}' with columns:")
            for col in df.columns:
                print(f"  - {col}")
            
            # Save to database
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            
            # Verify table creation
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"Verified table '{table_name}' with {row_count} rows")
        
        # Print final database state
        print("\nFinal Database Tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  - {table[0]} ({count} rows)")
        
        # Create backup of database
        backup_path = f"{db_path}.backup"
        with sqlite3.connect(backup_path) as backup:
            conn.backup(backup)
        print(f"\nCreated backup at: {backup_path}")
        
        conn.close()
        print("\nDatabase creation completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during database creation: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    # In production (Render), use the deployed Excel file
    if os.environ.get('RENDER'):
        excel_path = "/opt/render/project/src/hardware_data.xlsx"
    else:
        excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hardware_data.xlsx')
    
    create_and_load_database(excel_path)
