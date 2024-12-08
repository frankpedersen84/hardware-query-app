# Hardware Query Application

A Flask-based web application that allows users to query hardware and camera data using natural language. The application uses OpenAI's GPT model to convert natural language queries into SQL and retrieve information from a SQLite database containing camera and hardware information.

## Features
- Natural language querying of camera hardware data
- Automatic SQL query generation using GPT
- Comprehensive database of camera information
- Clean web interface for query input and results display

## Local Setup

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd excel_query_app
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

5. Place your hardware_data.xlsx file in the root directory

6. Initialize the database:
   ```bash
   python create_db.py
   ```

7. Run the application:
   ```bash
   python app.py
   ```

## Deployment to Render

1. Fork or push this repository to your GitHub account

2. Create a new Web Service on Render:
   - Connect your GitHub repository
   - Select the Python environment
   - The build and start commands are already configured in `render.yaml`

3. Add Environment Variables on Render:
   - Add your `OPENAI_API_KEY` in the Render dashboard
   - The `PORT` and `RENDER` variables are automatically set in render.yaml

4. Deploy:
   - Render will automatically deploy your application
   - The build process will:
     1. Install dependencies
     2. Copy the Excel file to the correct location
     3. Initialize the database
     4. Start the Flask application with gunicorn

5. Monitor:
   - Watch the build logs in Render's dashboard
   - Check the deployment status and logs
   - Verify database initialization

## Database Structure
The application uses a SQLite database with the following tables:
- hardware: Main hardware information
- cameras: Camera-specific details
- hardwaregeneralsettings: General hardware settings
- hardwareptzsettings: PTZ camera settings
- camerastreams: Stream configurations
- cameraevents: Event settings
- cameragroups: Camera grouping information

## Security Notes
- Never commit the `.env` file to version control
- Keep your OpenAI API key secure
- The application uses SQLite, ensure proper file permissions
- Consider adding authentication for production use

## Troubleshooting
If you encounter issues:
1. Check the logs in the `logs` directory
2. Verify the Excel file is properly formatted
3. Ensure all environment variables are set
4. Check the database initialization logs

## Support
For support or questions, please open an issue in the GitHub repository.
