#!/bin/bash

echo "=== PRE-START SCRIPT ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"

# Create logs directory if it doesn't exist
mkdir -p logs
chmod 777 logs

# Verify Excel file exists
if [ ! -f "hardware_data.xlsx" ]; then
    echo "Error: hardware_data.xlsx not found!"
    exit 1
fi

# Initialize database
echo "Initializing database..."
python create_db.py

# Verify database
echo "Verifying database..."
python check_db.py

echo "Pre-start completed successfully"
