#!/bin/bash

# Make scripts executable
chmod +x prestart.sh

# Run prestart script
./prestart.sh

# Start gunicorn with configuration file
exec gunicorn wsgi_app:application -c gunicorn.conf.py
