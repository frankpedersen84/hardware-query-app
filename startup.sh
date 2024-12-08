#!/bin/bash

# Initialize the database
python create_db.py

# Start the application
exec gunicorn app:app
