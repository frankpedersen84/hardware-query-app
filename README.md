# Hardware Query Application

A Flask-based web application that allows users to query hardware and camera data using natural language.

## Setup Instructions

1. Clone this repository
2. Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Deployment Options

### Option 1: Deploy to PythonAnywhere (Recommended for beginners)
1. Create an account at [PythonAnywhere](https://www.pythonanywhere.com/)
2. Upload your files to PythonAnywhere
3. Create a new web app using Flask
4. Set your working directory to the app directory
5. Set WSGI configuration file to point to wsgi.py
6. Add your environment variables in the PythonAnywhere dashboard

### Option 2: Deploy to Heroku
1. Install Heroku CLI
2. Create a new Heroku app
3. Set your environment variables in Heroku dashboard
4. Deploy using Git:
   ```bash
   heroku login
   git init
   git add .
   git commit -m "Initial commit"
   heroku git:remote -a your-app-name
   git push heroku master
   ```

### Option 3: Self-hosted with Gunicorn (Linux/Unix)
1. Install Gunicorn:
   ```bash
   pip install gunicorn
   ```
2. Run with Gunicorn:
   ```bash
   gunicorn --bind 0.0.0.0:8000 wsgi:app
   ```

## Security Notes
- Keep your `.env` file secure and never commit it to version control
- The OpenAI API key should be kept private
- Consider adding authentication if needed
- Regularly update dependencies for security patches

## Support
For support or questions, please contact the development team.
