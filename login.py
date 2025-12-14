import streamlit as st
import os

# --- CLERK CONFIGURATION (MUST MATCH app.py) ---
CLERK_PUBLISHABLE_KEY = "pk_test_ZGVjZW50LXBpcmFuaGEtMTQuY2xlcmsuYWNjb3VudHMuZGV2JA"
APP_URL = os.getenv("APP_URL", "http://localhost:8501") 

def get_clerk_redirect_url(pathname):
    """Generates the full Clerk URL for sign-in/sign-up."""
    domain = CLERK_PUBLISHABLE_KEY.split('_')[1]
    # Clerk redirects back to APP_URL with the __session token attached
    return f"https://{domain}.clerk.accounts.dev/{pathname}?redirect_url={APP_URL}"

# --- STREAMLIT UI ---

st.set_page_config(page_title="Clerk Login", page_icon="🔑", layout="centered")

st.title("🔐 Secure Authentication")
st.markdown("Click the buttons below to sign in or sign up using **Clerk**.")
st.caption("You will be redirected to a secure, external page.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.link_button(
        "🔑 Sign In", 
        url=get_clerk_redirect_url("sign-in"),
        type="primary"
    )

with col2:
    st.link_button(
        "📝 Sign Up", 
        url=get_clerk_redirect_url("sign-up")
    )

st.divider()

st.page_link("app.py", label="⬅️ Back to Chatbot")