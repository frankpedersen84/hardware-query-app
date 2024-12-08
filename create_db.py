import pandas as pd
import sqlite3
import os
from logging_config import setup_logging

logger = setup_logging('database.log')

def create_and_load_database(excel_path, db_path='hardware.db'):
    print("\n=== Database Creation Process ===")
    print(f"Reading Excel file from: {excel_path}")
    logger.info("=== Database Creation Process ===")
    logger.info(f"Reading Excel file from: {excel_path}")
    logger.info(f"Creating database at: {db_path}")
    
    # Check if Excel file exists
    if not os.path.exists(excel_path):
        error_msg = f"Error: Excel file not found at {excel_path}"
        print(error_msg)
        logger.error(error_msg)
        print("\nListing directory contents:")
        dir_path = os.path.dirname(excel_path)
        print(f"Contents of {dir_path}:")
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            if os.path.isfile(item_path):
                print(f"  - {item} (file, {os.path.getsize(item_path)} bytes)")
            else:
                print(f"  - {item} (directory)")
        return False
    
    print(f"Excel file exists, size: {os.path.getsize(excel_path)} bytes")
    logger.info(f"Excel file exists, size: {os.path.getsize(excel_path)} bytes")
    
    try:
        # Create/connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Drop all existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
        conn.commit()
        
        # Read Excel file
        print("\nReading Excel file...")
        excel_file = pd.ExcelFile(excel_path)
        print("\nAvailable sheets in Excel:")
        for sheet in excel_file.sheet_names:
            print(f"  - {sheet}")
        logger.info("\nAvailable sheets in Excel:")
        for sheet in excel_file.sheet_names:
            logger.info(f"  - {sheet}")
        
        # Process each sheet
        for sheet_name in excel_file.sheet_names:
            print(f"\nProcessing sheet: {sheet_name}")
            logger.info(f"\nProcessing sheet: {sheet_name}")
            df = pd.read_excel(excel_file, sheet_name)
            
            # Print data info
            print(f"\nDataset Info for {sheet_name}:")
            print(f"Total rows: {len(df)}")
            print(f"Total columns: {len(df.columns)}")
            print("\nColumns and sample values:")
            for col in df.columns:
                sample_values = df[col].head(3).tolist()
                print(f"  - {col}: {sample_values}")
            logger.info(f"\nDataset Info for {sheet_name}:")
            logger.info(f"Total rows: {len(df)}")
            logger.info(f"Total columns: {len(df.columns)}")
            logger.info("\nColumns and sample values:")
            for col in df.columns:
                sample_values = df[col].head(3).tolist()
                logger.info(f"  - {col}: {sample_values}")
            
            # Print first few rows
            print("\nFirst few rows:")
            print(df.head().to_string())
            logger.debug("\nFirst few rows:")
            logger.debug(df.head().to_string())
            
            # Clean column names (remove spaces, special chars)
            original_columns = list(df.columns)
            df.columns = [col.strip().lower().replace(' ', '_').replace('-', '_') for col in df.columns]
            
            # Log column name changes
            for orig, new in zip(original_columns, df.columns):
                if orig != new:
                    print(f"Column renamed: '{orig}' -> '{new}'")
                    logger.info(f"Column renamed: '{orig}' -> '{new}'")
            
            # Clean table name
            table_name = sheet_name.strip().lower().replace(' ', '_').replace('-', '_')
            print(f"\nCreating table '{table_name}' with columns:")
            for col in df.columns:
                print(f"  - {col}")
            logger.info(f"\nCreating table '{table_name}' with columns:")
            for col in df.columns:
                logger.info(f"  - {col}")
            
            # Save to database
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            
            # Verify table creation
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"\nVerified table '{table_name}' with {row_count} rows")
            logger.info(f"\nVerified table '{table_name}' with {row_count} rows")
        
        # Print final database state
        print("\nFinal Database Tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  - {table[0]} ({count} rows)")
            logger.info(f"  - {table[0]} ({count} rows)")
            
            # Log table schema
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            print(f"    Columns: {', '.join(col[1] for col in columns)}")
            logger.info(f"    Columns: {', '.join(col[1] for col in columns)}")
        
        # Create backup of database
        backup_path = f"{db_path}.backup"
        with sqlite3.connect(backup_path) as backup:
            conn.backup(backup)
        print(f"\nCreated backup at: {backup_path}")
        logger.info(f"\nCreated backup at: {backup_path}")
        
        conn.close()
        print("\nDatabase creation completed successfully!")
        logger.info("\nDatabase creation completed successfully!")
        return True
        
    except Exception as e:
        error_msg = f"Error during database creation: {str(e)}"
        print(error_msg)
        logger.error(error_msg, exc_info=True)
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    # In production (Render), use the deployed Excel file
    if os.environ.get('RENDER'):
        excel_path = "/opt/render/project/src/hardware_data.xlsx"
    else:
        # Try to find the Excel file in multiple locations
        possible_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hardware_data.xlsx'),
            r"C:\Users\Admin-Frankie\Desktop\hardware.xlsx"
        ]
        
        excel_path = None
        for path in possible_paths:
            if os.path.exists(path):
                excel_path = path
                break
                
        if not excel_path:
            print("Error: Could not find Excel file in any of these locations:")
            for path in possible_paths:
                print(f"  - {path}")
            exit(1)
    
    create_and_load_database(excel_path)
