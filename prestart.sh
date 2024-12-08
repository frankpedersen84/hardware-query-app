#!/bin/bash

echo "=== PRE-START SCRIPT ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"

# Create logs directory
mkdir -p /var/log
chmod 777 /var/log

# Verify Excel file
echo "Checking Excel file..."
if [ -f "hardware_data.xlsx" ]; then
    echo "Excel file exists"
    ls -l hardware_data.xlsx
else
    echo "ERROR: Excel file not found!"
    exit 1
fi

# Initialize database
echo "Creating database..."
python create_db.py

# Verify database
echo "Verifying database..."
python check_db.py

echo "Pre-start script completed"
