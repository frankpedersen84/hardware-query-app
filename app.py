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

# Configure OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Use absolute paths for database
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hardware.db')

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
            sample_dict = {}
            for i, col in enumerate(columns):
                sample_dict[col[1]] = sample[i]
            schema[f"{table_name}_sample"] = sample_dict
    
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
- The Hardware table contains device information with columns:
  * Name (e.g., 'Camp East (10.101.112.109)')
  * Address (e.g., 'http://10.101.112.109/')
  * Model (e.g., 'Pelco IMM12027')
  * FirmwareVersion (e.g., '2.10.0.13.8360-A0.0')
- The Cameras table contains camera information with columns:
  * Name (e.g., 'Camp East Classroom Door 109')
  * Hardware (links to Hardware.Name)
  * Address (e.g., 'http://10.101.112.109/')
  * Channel (numeric)
- Common patterns in the data:
  * Hardware names include IP: 'Camp East (10.101.112.109)'
  * Camera names are descriptive: 'Camp East Classroom Door 109'
  * Addresses are full URLs: 'http://10.101.112.109/'
- Example queries:
  * "What is the IP address of Camp East?" →
    SELECT REPLACE(REPLACE(Address, 'http://', ''), '/', '') as IP 
    FROM Hardware 
    WHERE Name LIKE 'Camp East%';
  * "Show me all cameras in Camp East" →
    SELECT Name, Channel
    FROM Cameras 
    WHERE Hardware LIKE 'Camp East%'
    ORDER BY Channel;
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
