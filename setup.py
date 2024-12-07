from setuptools import setup, find_packages

setup(
    name="hardware-query-app",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'Flask>=2.3.3',
        'Werkzeug>=2.3.7',
        'numpy>=1.24.3',
        'pandas>=2.0.3',
        'openpyxl>=3.1.2',
        'openai>=1.0.0',
        'python-dotenv>=1.0.0',
        'gunicorn>=21.2.0',
        'SQLAlchemy>=2.0.21',
        'Flask-SQLAlchemy>=3.1.1'
    ],
)
