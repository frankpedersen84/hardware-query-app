import sqlite3

def run_test_queries():
    conn = sqlite3.connect('hardware.db')
    cursor = conn.cursor()
    
    # Test queries
    queries = [
        "SELECT name, Address FROM Hardware LIMIT 5;",
        "SELECT DISTINCT Hardware FROM Cameras LIMIT 5;",
        "SELECT Name FROM Cameras WHERE Hardware LIKE '%Camp East%' LIMIT 5;",
        "SELECT DISTINCT Name FROM Hardware WHERE Name LIKE '%Camp%' LIMIT 5;"
    ]
    
    for query in queries:
        print(f"\nExecuting query: {query}")
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            print("Results:")
            for row in results:
                print(row)
        except Exception as e:
            print(f"Error: {str(e)}")
    
    conn.close()

if __name__ == "__main__":
    run_test_queries()
