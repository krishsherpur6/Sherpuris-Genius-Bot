import psycopg2

# Your Config
DB_CONFIG = {
    "dbname": "genius_bot_db", 
    "user": "postgres",        
    "password": "sherpuriii",  
    "host": "localhost",       
    "port": "5432"
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("🗑️  Deleting old table...")
    cur.execute("DROP TABLE IF EXISTS search_history")
    
    print("✨ Creating new table with correct columns...")
    cur.execute("""
        CREATE TABLE search_history (
            id SERIAL PRIMARY KEY, 
            query TEXT, 
            response TEXT, 
            timestamp TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database successfully fixed! You can run app.py now.")

except Exception as e:
    print(f"❌ Error: {e}")