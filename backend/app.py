from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import psycopg2
import datetime

app = Flask(__name__)
# Allow all origins to fix connection issues
CORS(app, resources={r"/*": {"origins": "*"}})

# --- CONFIGURATION ---
GOOG_API_KEY = "AIzaSyCDIB12k84JmdNfiWzd19JHO8em8FiaMmE"
DB_CONFIG = {
    "dbname": "genius_bot_db", 
    "user": "postgres",        
    "password": "sherpuriii",  
    "host": "localhost",       
    "port": "5432"
}

# --- SETUP AI ---
genai.configure(api_key=GOOG_API_KEY)

def get_working_model():
    """Finds a valid model that supports content generation."""
    try:
        print("🔍 Checking available models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Prefer specific models if available
                if 'gemini-1.5-flash' in m.name:
                    print(f"✅ Found preferred model: {m.name}")
                    return genai.GenerativeModel(m.name)
                elif 'gemini-pro' in m.name:
                    print(f"✅ Found standard model: {m.name}")
                    return genai.GenerativeModel(m.name)
        
        # Fallback
        print("⚠️ No specific match found, trying default 'gemini-pro'")
        return genai.GenerativeModel('gemini-pro')
    except Exception as e:
        print(f"❌ Model listing failed: {e}")
        return genai.GenerativeModel('gemini-pro')

# Initialize Model
model = get_working_model()

def get_db_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"❌ Database Connection Failed: {e}")
        return None

@app.route('/chat', methods=['POST'])
def chat():
    print("\n--- NEW REQUEST ---")
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "No message"}), 400

    try:
        # 1. Generate AI Response
        print(f"📩 User: {user_message}")
        response = model.generate_content(user_message)
        ai_response = response.text
        print(f"🤖 AI: {ai_response[:50]}...")
        
        # 2. Save to Postgres
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            
            # Ensure table exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id SERIAL PRIMARY KEY, 
                    query TEXT, 
                    response TEXT, 
                    timestamp TIMESTAMP
                )
            """)
            
            timestamp = datetime.datetime.now()
            cur.execute(
                "INSERT INTO search_history (query, response, timestamp) VALUES (%s, %s, %s)",
                (user_message, ai_response, timestamp)
            )
            conn.commit()
            cur.close()
            conn.close()
            
        return jsonify({"response": ai_response})

    except Exception as e:
        error_msg = str(e)
        print(f"❌ ERROR: {error_msg}")
        
        # Fallback: If the auto-selected model failed, try 'gemini-pro' directly
        if "404" in error_msg:
             try:
                 print("🔄 Retrying with fallback model 'gemini-pro'...")
                 fallback = genai.GenerativeModel('gemini-pro')
                 res = fallback.generate_content(user_message)
                 return jsonify({"response": res.text})
             except Exception as e2:
                 return jsonify({"response": f"Error: {str(e2)}"})
        
        return jsonify({"response": f"Sorry, error: {error_msg}"})

if __name__ == '__main__':
    # Force IPv4 to fix connection issues
    print("🚀 Backend running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000, host='127.0.0.1')
