import pandas as pd
import sqlite3

# Define the new data
data = {
    'name': ['Camera 1', 'Camera 2', 'Camera 3', 'DVR System', 'NVR System', 'Camp East'],
    'ip_address': ['192.168.1.100', '192.168.1.101', '192.168.1.102', '192.168.1.200', '192.168.1.201', '192.168.1.103'],
    'shortcut': ['CAM1', 'CAM2', 'CAM3', 'DVR1', 'NVR1', 'CAMP1'],
    'firmware_version': ['v2.1.0', 'v2.1.0', 'v2.0.9', 'v3.2.1', 'v4.0.0', 'v2.1.1'],
    'unit': ['Main Building', 'Warehouse', 'Parking Lot', 'Security Room', 'IT Room', 'East Campus']
}

# Create DataFrame and save to Excel
df = pd.DataFrame(data)
df.to_excel('hardware_data.xlsx', index=False)
print("Excel file updated")

# Update database
conn = sqlite3.connect('hardware.db')
df.to_sql('hardware', conn, if_exists='replace', index=False)
print("Database updated")

# Verify data
cursor = conn.cursor()
cursor.execute("SELECT * FROM hardware WHERE name = 'Camp East'")
print("\nVerifying Camp East data:")
print(cursor.fetchall())

conn.close()
