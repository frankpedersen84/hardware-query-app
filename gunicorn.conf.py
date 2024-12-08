# Gunicorn configuration file
import os

# Get port from environment variable
port = os.getenv("PORT", "10000")

# Bind to 0.0.0.0 to allow external access
bind = f"0.0.0.0:{port}"

# Number of worker processes
workers = 4

# Timeout in seconds
timeout = 120

# The WSGI application to use
wsgi_app = "wsgi_app:application"

# Override any command-line arguments
raw_env = [
    "GUNICORN_CMD_ARGS=--config gunicorn.conf.py"
]
