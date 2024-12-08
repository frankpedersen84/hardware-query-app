import sqlite3

def check_database():
    print("\n=== Database Check ===")
    conn = sqlite3.connect('hardware.db')
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("\nTables in database:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"\n=== {table[0]} ({count} rows) ===")
        
        # Get schema
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print("Columns:", [col[1] for col in columns])
        
        # Print first few rows
        cursor.execute(f"SELECT * FROM {table[0]} LIMIT 3")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    
    conn.close()

if __name__ == "__main__":
    check_database()
