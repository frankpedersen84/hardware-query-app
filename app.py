from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import sqlite3
import json
import os
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix
from create_db import create_and_load_database

# Load environment variables
load_dotenv()

if not os.getenv('OPENAI_API_KEY'):
    raise ValueError("OPENAI_API_KEY must be set in .env file")

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Configure for production
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

# Configure OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Use absolute paths for database and Excel file
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hardware.db')
if os.environ.get('RENDER'):
    EXCEL_PATH = "/opt/render/project/src/hardware.xlsx"
else:
    EXCEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hardware.xlsx')

# Initialize database on startup
if os.environ.get('RENDER'):
    print("Running on Render, checking Excel file...")
    excel_path = "/opt/render/project/src/hardware.xlsx"
    if os.path.exists(excel_path):
        print(f"Excel file found at {excel_path}")
        print(f"File size: {os.path.getsize(excel_path)} bytes")
    else:
        print(f"Excel file NOT found at {excel_path}")
        print("Listing directory contents:")
        print(os.listdir("/opt/render/project/src/"))
else:
    excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hardware.xlsx')
    
print(f"Initializing database from {excel_path}")
success = create_and_load_database(excel_path, DATABASE_PATH)
if success:
    print("Database initialized successfully")
    # Print all tables in the database
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in database:", [table[0] for table in tables])
else:
    print("Failed to initialize database")

def get_db_connection():
    """Get a connection to the database"""
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
        
        schema_context = "Database tables and their columns:\n"
        for table_name, columns in schema.items():
            schema_context += f"\nTable '{table_name}':\n"
            schema_context += "Columns: " + ", ".join(columns) + "\n"
        
        prompt = f"""Given this database schema:
{schema_context}

Convert this natural language query to SQL:
"{query}"

Important notes:
- Return ONLY the SQL query, no explanations
- The Hardware table contains device information with columns:
  * Name (e.g., 'Camp East (10.101.112.109)')
  * Address (e.g., 'http://10.101.112.109/')
  * Model (e.g., 'Pelco IMM12027')
  * FirmwareVersion (e.g., '2.10.0.13.8360-A0.0')
- Example queries:
  * "What is the IP address of Camp East?" →
    SELECT REPLACE(REPLACE(Address, 'http://', ''), '/', '') as IP 
    FROM Hardware 
    WHERE Name LIKE 'Camp East%';
  * "Show me all cameras in Camp East" →
    SELECT c.Name, c.Channel
    FROM Cameras c
    WHERE c.Hardware LIKE 'Camp East%'
    ORDER BY c.Channel;
  * "What is the firmware version of Camp East?" →
    SELECT FirmwareVersion 
    FROM Hardware 
    WHERE Name LIKE 'Camp East%';
  * "Show me all cameras in Unit 5" →
    SELECT c.Name, c.Channel
    FROM Cameras c
    WHERE c.Hardware LIKE 'Unit 5%'
    ORDER BY c.Channel;"""

        # Make the API call
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a SQL expert. Generate only SQL queries without any explanations or comments."},
                    {"role": "user", "content": prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0
            )
            sql_query = response.choices[0].message.content.strip()
            print(f"Generated SQL query: {sql_query}")  # Debug print
            
            # Execute the query
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query)
            columns = [description[0] for description in cursor.description]
            results = cursor.fetchall()
            conn.close()
            
            # Format results
            formatted_results = []
            for row in results:
                formatted_results.append(dict(zip(columns, row)))
                
            return {
                "status": "success",
                "query": sql_query,
                "results": formatted_results
            }
            
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            return {"status": "error", "message": f"Database error: {str(e)}"}
        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
            return {"status": "error", "message": f"OpenAI API error: {str(e)}"}
            
    except Exception as e:
        print(f"Query processing error: {str(e)}")
        return {"status": "error", "message": f"Query processing error: {str(e)}"}

@app.route('/')
def home():
    """Render the home page"""
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    """Handle natural language query"""
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"status": "error", "message": "No query provided"})
    return jsonify(process_natural_language_query(data['query']))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
