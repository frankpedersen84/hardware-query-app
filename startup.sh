#!/bin/bash

# Create logs directory
mkdir -p logs

# Print environment info
echo "Starting application..."
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Directory contents:"
ls -la

# Initialize the database
echo "Initializing database..."
python create_db.py

# Start the application
echo "Starting Flask application..."
gunicorn app:app --bind 0.0.0.0:$PORT --log-file logs/gunicorn.log --access-logfile logs/access.log --error-logfile logs/error.log
