from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import sqlite3
import json
import os
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

# Load environment variables
load_dotenv()

if not os.getenv('OPENAI_API_KEY'):
    raise ValueError("OPENAI_API_KEY must be set in .env file")

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Configure for production
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_table_schema():
    """Get the schema of all tables in the database"""
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    schema = {}
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        schema[table_name] = [col[1] for col in columns]  # Get column names
    
    conn.close()
    return schema

def process_natural_language_query(query):
    """Process natural language query using GPT and convert to SQL"""
    try:
        # Get database schema
        schema = get_table_schema()
        
        # Create context for GPT
        schema_context = "Database tables and columns:\n"
        for table, columns in schema.items():
            schema_context += f"Table '{table}': {', '.join(columns)}\n"
        
        # Create prompt for GPT
        prompt = f"""Given this database schema:
{schema_context}

Convert this natural language query to SQL:
"{query}"

Important notes:
- The Hardware table contains device information (Name, Address, etc.)
- The Cameras table contains camera details
- Tables are linked by the Hardware and Name fields
- Return ONLY the SQL query, no explanations

Example queries:
1. "What is the IP address of camera Camp East?" →
   SELECT h.Address FROM Hardware h WHERE h.Name LIKE '%Camp East%';
   
2. "What is the shortcut for Camp East Classroom Door 109?" →
   SELECT c.Shortcut FROM Cameras c WHERE c.Name = 'Camp East Classroom Door 109';"""

        # Get SQL query from GPT
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        sql_query = response.choices[0].message.content.strip()
        
        # Execute the SQL query
        conn = sqlite3.connect('excel_data.db')
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
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

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

if __name__ == '__main__':
    app.run()
