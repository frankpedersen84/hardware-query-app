#!/bin/bash

# Initialize the database
python create_db.py

# Create logs directory
mkdir -p logs

# Start the application with logging
echo "Starting application..."
echo "Current directory: $(pwd)"
echo "Listing files:"
ls -la

echo "Starting gunicorn..."
exec gunicorn app:app 2>&1 | tee -a logs/gunicorn.log
