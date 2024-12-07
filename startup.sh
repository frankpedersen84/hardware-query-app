#!/bin/bash

echo "=== STARTUP SCRIPT ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"

# Create logs directory
mkdir -p logs
chmod 777 logs

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

# Start the application
echo "Starting Flask application..."
gunicorn app:app --bind 0.0.0.0:${PORT:-10000} --log-file logs/gunicorn.log --access-logfile logs/access.log --error-logfile logs/error.log --capture-output --enable-stdio-inheritance
