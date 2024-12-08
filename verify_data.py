import pandas as pd
import sqlite3
import os

# Define paths
EXCEL_PATH = 'hardware_data.xlsx'
DB_PATH = 'hardware.db'

# Read Excel file
print("Reading Excel file...")
df = pd.read_excel(EXCEL_PATH)
print("\nExcel Data:")
print(df)

# Connect to database and create table
print("\nCreating database...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS hardware (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        ip_address TEXT,
        shortcut TEXT,
        firmware_version TEXT,
        unit TEXT
    )
''')

# Load data into database
print("\nLoading data into database...")
df.to_sql('hardware', conn, if_exists='replace', index=False)

# Verify data in database
print("\nVerifying database data:")
cursor.execute("SELECT * FROM hardware")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
