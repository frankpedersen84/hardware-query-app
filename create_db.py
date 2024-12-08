import pandas as pd
import sqlite3
import os
from logging_config import setup_logging

logger = setup_logging('database.log')

def create_and_load_database(excel_path, db_path='hardware.db'):
    logger.info("=== Database Creation Process ===")
    logger.info(f"Reading Excel file from: {excel_path}")
    logger.info(f"Creating database at: {db_path}")
    
    try:
        # Create/connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read Excel file
        excel_file = pd.ExcelFile(excel_path)
        logger.info("\nAvailable sheets in Excel:")
        for sheet in excel_file.sheet_names:
            logger.info(f"  - {sheet}")
        
        # Process each sheet
        for sheet_name in excel_file.sheet_names:
            logger.info(f"\nProcessing sheet: {sheet_name}")
            df = pd.read_excel(excel_file, sheet_name)
            
            # Print raw data sample
            logger.debug(f"Sample data from sheet {sheet_name}:")
            logger.debug(df.head().to_string())
            
            # Clean column names (remove spaces, special chars)
            original_columns = list(df.columns)
            df.columns = [col.strip().lower().replace(' ', '_').replace('-', '_') for col in df.columns]
            
            # Log column name changes
            for orig, new in zip(original_columns, df.columns):
                if orig != new:
                    logger.info(f"Column renamed: '{orig}' -> '{new}'")
            
            # Create table name from sheet name (clean it up)
            original_table_name = sheet_name
            table_name = sheet_name.strip().lower().replace(' ', '_').replace('-', '_')
            if original_table_name != table_name:
                logger.info(f"Table name cleaned: '{original_table_name}' -> '{table_name}'")
            
            # Print schema information
            logger.info(f"Creating table '{table_name}' with columns:")
            for col in df.columns:
                logger.info(f"  - {col}")
            
            # Save to database
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            
            # Verify table creation
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            logger.info(f"Verified table '{table_name}' with {row_count} rows")
        
        # Print final database state
        logger.info("\nFinal Database Tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            logger.info(f"  - {table[0]} ({count} rows)")
            
            # Log table schema
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            logger.info(f"    Columns: {', '.join(col[1] for col in columns)}")
        
        # Create backup of database
        backup_path = f"{db_path}.backup"
        with sqlite3.connect(backup_path) as backup:
            conn.backup(backup)
        logger.info(f"\nCreated backup at: {backup_path}")
        
        conn.close()
        logger.info("\nDatabase creation completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during database creation: {str(e)}", exc_info=True)
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
