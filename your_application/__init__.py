from flask import Flask, render_template, request, jsonify
import openai
import sqlite3
import json
import os
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix
import pandas as pd

# Load environment variables
load_dotenv()

if not os.getenv('OPENAI_API_KEY'):
    raise ValueError("OPENAI_API_KEY must be set in .env file")

app = Flask(__name__, 
           template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'),
           static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Configure for production
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Use absolute paths for both database and Excel file
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'hardware.db')
EXCEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'hardware_data.xlsx')

def init_db():
    """Initialize the database and create tables if they don't exist"""
    try:
        if not os.path.exists(DATABASE_PATH):
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hardware (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    ip_address TEXT,
                    shortcut TEXT,
                    firmware_version TEXT,
                    unit TEXT
                )
            ''')
            
            # Only try to load Excel data if the file exists
            if os.path.exists(EXCEL_PATH):
                try:
                    df = pd.read_excel(EXCEL_PATH)
                    df.to_sql('hardware', conn, if_exists='replace', index=False)
                    print(f"Successfully loaded data from {EXCEL_PATH}")
                except Exception as e:
                    print(f"Warning: Could not load Excel data: {e}")
            else:
                print(f"Note: Excel file not found at {EXCEL_PATH}. Using existing database if available.")
            
            conn.commit()
            conn.close()
        else:
            print(f"Using existing database at {DATABASE_PATH}")
    except Exception as e:
        print(f"Database initialization error: {e}")

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_table_schema():
    """Get the schema of all tables in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    schema = {}
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        schema[table_name] = [col[1] for col in columns]
    
    conn.close()
    return schema

def process_natural_language_query(query):
    """Process natural language query using GPT and convert to SQL"""
    try:
        schema = get_table_schema()
        
        schema_context = "Database tables and columns:\n"
        for table, columns in schema.items():
            schema_context += f"Table '{table}': {', '.join(columns)}\n"
        
        prompt = f"""Given this database schema:
{schema_context}

Convert this natural language query to SQL:
"{query}"

Important notes:
- The Hardware table contains device information (Name, Address, etc.)
- The Cameras table contains camera details
- Tables are linked by the Hardware and Name fields
- Return ONLY the SQL query, no explanations"""

        # Make the API call
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            sql_query = response['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
            return {"status": "error", "message": "Failed to process query"}
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        columns = [description[0] for description in cursor.description]
        results = cursor.fetchall()
        conn.close()
        
        formatted_results = []
        for row in results:
            formatted_results.append(dict(zip(columns, row)))
            
        return {
            "status": "success",
            "query": sql_query,
            "results": formatted_results
        }
    except Exception as e:
        print(f"Query processing error: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    query_text = request.json.get('query')
    if not query_text:
        return jsonify({"error": "No query provided"}), 400
    
    result = process_natural_language_query(query_text)
    return jsonify(result)

# Initialize database on startup
init_db()
