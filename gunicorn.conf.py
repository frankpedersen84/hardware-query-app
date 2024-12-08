# Gunicorn configuration file
bind = "0.0.0.0:10000"
wsgi_app = "wsgi:app"
workers = 4
timeout = 120
