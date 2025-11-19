import streamlit as st
import google.generativeai as genai
import psycopg2
import datetime
import bcrypt
import time  # <--- ADDED THIS for the "wait" trick
from psycopg2.extras import RealDictCursor

# --- 1. CONFIGURATION & CREDENTIALS ---
st.set_page_config(page_title="Sherpuri's Genius Bot", page_icon="⚡", layout="wide")

# 🌟 GEMINI API KEY 🌟
GOOG_API_KEY = "AIzaSyCDIB12k84JmdNfiWzd19JHO8em8FiaMmE"

# 🐘 POSTGRESQL DATABASE CREDENTIALS 🐘
DB_CONFIG = {
    "dbname": "genius_bot_db", 
    "user": "postgres",        
    "password": "sherpuriii",  
    "host": "localhost",       
    "port": "5432"
}

# --- 2. DATABASE FUNCTIONS ---
def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"❌ Database Connection Error: {e}")
        st.stop()

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            user_query TEXT,
            ai_response TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

def save_to_db(user_id, query, response):
    conn = get_db_connection()
    cur = conn.cursor()
    timestamp = datetime.datetime.now()
    cur.execute(
        "INSERT INTO search_history (user_id, user_query, ai_response, timestamp) VALUES (%s, %s, %s, %s)",
        (user_id, query, response, timestamp)
    )
    conn.commit()
    cur.close()
    conn.close()

# --- 3. AUTHENTICATION FUNCTIONS ---
def register_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_pw))
        conn.commit()
        st.success("✅ Account created! Please log in.")
    except psycopg2.errors.UniqueViolation:
        st.error("⚠️ Username already exists.")
        conn.rollback()
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

def login_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return user['id'], user['username']
    else:
        return None, None

def get_user_history(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT user_query, timestamp FROM search_history WHERE user_id = %s ORDER BY id DESC LIMIT 10", (user_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

# --- INIT ---
init_db()
try:
    genai.configure(api_key=GOOG_API_KEY)

    model = genai.GenerativeModel('gemini-2.0-flash')
except:
    st.error("Error configuring API Key")

# --- 4. MAIN APP LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("⚡ Sherpuri's Genius Bot")
    st.subheader("Please Login")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("Login"):
            uid, uname = login_user(u, p)
            if uid:
                st.session_state.logged_in = True
                st.session_state.user_id = uid
                st.session_state.username = uname
                st.rerun()
            else:
                st.error("❌ Failed")
    with tab2:
        nu = st.text_input("New Username", key="r_u")
        np = st.text_input("New Password", type="password", key="r_p")
        if st.button("Create Account"):
            register_user(nu, np)
else:
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
        st.title(f"Hi, {st.session_state.username}!")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        st.subheader("📜 History")
        hist = get_user_history(st.session_state.user_id)
        if hist:
            for h in hist:
                st.caption(f"🕒 {h['timestamp'].strftime('%H:%M')}")
                st.info(h['user_query'])

    st.header("⚡ Sherpuri's Genius Bot")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        avatar = "👤" if m["role"] == "user" else "⚡"
        with st.chat_message(m["role"], avatar=avatar):
            st.markdown(m["content"])

    prompt = st.chat_input("Ask away...")
    if prompt:
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            with st.chat_message("assistant", avatar="⚡"):
                with st.spinner("Thinking..."):
                    # --- AUTO-RETRY LOGIC (The Fix for 429 Errors) ---
                    response_text = ""
                    for attempt in range(3): # Try 3 times
                        try:
                            chat = model.start_chat(history=[
                                {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                                for m in st.session_state.messages[:-1]
                            ])
                            response = chat.send_message(prompt)
                            response_text = response.text
                            break # Success! Exit loop
                        except Exception as e:
                            if "429" in str(e):
                                time.sleep(4) # Wait 4 seconds and try again
                                continue
                            else:
                                raise e # If it's another error, crash.
                    
                    if response_text:
                        st.markdown(response_text)
                        save_to_db(st.session_state.user_id, prompt, response_text)
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        st.rerun()
                    else:
                        st.error("Server is too busy. Please wait 1 minute.")

        except Exception as e:
            st.error(f"Error: {e}")