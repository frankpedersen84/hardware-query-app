from flask import Flask, render_template, request, jsonify
import openai
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

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Use absolute paths for database
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'excel_data.db')

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
        
        # Get sample data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            schema[f"{table_name}_sample"] = dict(zip(schema[table_name], sample))
    
    conn.close()
    return schema

def process_natural_language_query(query):
    """Process natural language query using GPT and convert to SQL"""
    try:
        schema = get_table_schema()
        
        schema_context = "Database tables and their columns:\n"
        for table_name, columns in schema.items():
            if not table_name.endswith('_sample'):
                schema_context += f"\nTable '{table_name}':\n"
                schema_context += "Columns: " + ", ".join(columns) + "\n"
                if f"{table_name}_sample" in schema:
                    schema_context += "Sample data:\n"
                    for col, val in schema[f"{table_name}_sample"].items():
                        schema_context += f"  {col}: {val}\n"
        
        prompt = f"""Given this database schema:
{schema_context}

Convert this natural language query to SQL:
"{query}"

Important notes:
- Return ONLY the SQL query, no explanations
- The tables contain hardware and camera information
- Hardware and camera details are linked by Name fields
- Use JOIN operations when needed to combine data from multiple tables"""

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
    data = request.get_json()
    query = data.get('query', '')
    result = process_natural_language_query(query)
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
