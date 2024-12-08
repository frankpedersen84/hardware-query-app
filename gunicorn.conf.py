# Gunicorn configuration file
bind = "0.0.0.0:10000"
wsgi_app = "wsgi:app"
workers = 4
timeout = 120
# Override any command-line arguments
raw_env = [
    "GUNICORN_CMD_ARGS=--config gunicorn.conf.py"
]
