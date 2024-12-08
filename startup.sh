#!/bin/bash

# Initialize the database
python create_db.py

# Start the application
echo "Starting application..."
echo "Current directory: $(pwd)"
echo "Listing files:"
ls -la

echo "Starting gunicorn..."
gunicorn app:app
