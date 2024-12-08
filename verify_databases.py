import sqlite3
import os

def check_database(db_path):
    print(f"\nChecking database: {db_path}")
    if not os.path.exists(db_path):
        print(f"Database does not exist: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Found {len(tables)} tables:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\nTable: {table_name}")
            print(f"Row count: {count}")
            
            # Get schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            sample = cursor.fetchone()
            if sample:
                print("Sample row:")
                for col, val in zip([col[1] for col in columns], sample):
                    print(f"  {col}: {val}")
    
    except Exception as e:
        print(f"Error checking database: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Check both databases
    excel_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'excel_data.db')
    hardware_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hardware.db')
    
    check_database(excel_db)
    check_database(hardware_db)
