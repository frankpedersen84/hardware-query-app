import sqlite3
import os
import shutil

# First backup the current hardware.db just in case
if os.path.exists('hardware.db'):
    shutil.copy2('hardware.db', 'hardware.db.backup')

# Copy excel_data.db to hardware.db
shutil.copy2('excel_data.db', 'hardware.db')

# Verify the data
conn = sqlite3.connect('hardware.db')
cursor = conn.cursor()

print("Database contents:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"\nTable: {table[0]}")
    cursor.execute(f"SELECT * FROM {table[0]}")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

conn.close()
