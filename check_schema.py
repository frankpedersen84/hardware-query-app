import sqlite3

# Connect to database
conn = sqlite3.connect('excel_data.db')
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in database:")
for table in tables:
    print(f"\nTable: {table[0]}")
    cursor.execute(f"PRAGMA table_info({table[0]});")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Show first few rows
    cursor.execute(f"SELECT * FROM {table[0]} LIMIT 3")
    rows = cursor.fetchall()
    print("\nSample data:")
    for row in rows:
        print(row)

conn.close()
