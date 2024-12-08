import pandas as pd
import sqlite3
import os

# Get the absolute path to the database
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hardware.db')
EXCEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hardware_data.xlsx')

def create_database():
    # Create a new database connection
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Read all sheets from Excel file
        excel_file = pd.ExcelFile(EXCEL_PATH)
        
        # Create tables for each sheet
        for sheet_name in excel_file.sheet_names:
            # Read the sheet
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            # Clean column names (remove spaces, special characters)
            df.columns = [col.strip().replace(' ', '_').replace('(', '').replace(')', '') for col in df.columns]
            
            # Create table in SQLite
            df.to_sql(sheet_name, conn, if_exists='replace', index=False)
            print(f"Created table: {sheet_name}")
            
            # Print the schema
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({sheet_name})")
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            print()
    
    except Exception as e:
        print(f"Error: {str(e)}")
        conn.close()
        return False
    
    finally:
        conn.close()
    
    return True

def verify_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\nVerifying database contents:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"Table {table_name}: {count} rows")
            
            # Sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            sample = cursor.fetchone()
            if sample:
                print("Sample row:")
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                for col, val in zip(columns, sample):
                    print(f"  {col}: {val}")
            print()
    
    except Exception as e:
        print(f"Error during verification: {str(e)}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("Creating database from Excel workbook...")
    if create_database():
        print("\nDatabase created successfully!")
        verify_database()
    else:
        print("\nFailed to create database.")
