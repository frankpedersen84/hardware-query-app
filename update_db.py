import sqlite3

# Connect to database
conn = sqlite3.connect('hardware.db')
cursor = conn.cursor()

# Create table if it doesn't exist
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

# Insert sample data
data = [
    ('Camera 1', '192.168.1.100', 'CAM1', 'v2.1.0', 'Main Building'),
    ('Camera 2', '192.168.1.101', 'CAM2', 'v2.1.0', 'Warehouse'),
    ('Camera 3', '192.168.1.102', 'CAM3', 'v2.0.9', 'Parking Lot'),
    ('DVR System', '192.168.1.200', 'DVR1', 'v3.2.1', 'Security Room'),
    ('NVR System', '192.168.1.201', 'NVR1', 'v4.0.0', 'IT Room'),
    ('Camp East', '192.168.1.103', 'CAMP1', 'v2.1.1', 'East Campus')
]

# Clear existing data and insert new data
cursor.execute('DELETE FROM hardware')
cursor.executemany('INSERT INTO hardware (name, ip_address, shortcut, firmware_version, unit) VALUES (?, ?, ?, ?, ?)', data)

# Commit changes
conn.commit()

# Verify data
print("Database contents:")
cursor.execute('SELECT * FROM hardware')
for row in cursor.fetchall():
    print(row)

conn.close()
