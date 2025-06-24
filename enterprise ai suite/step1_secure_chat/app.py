import streamlit as st
from step1_secure_chat.auth import login_user, register_user
from step6_responsible_ai.privacy import mask_sensitive_data
from step6_responsible_ai.filters import is_safe_prompt
from step6_responsible_ai.auditor import log_audit
import requests
import json
from datetime import datetime

st.set_page_config(page_title="SmartEnterprise AI Suite", layout="wide")

if "username" not in st.session_state:
    st.session_state.username = None

def login_section():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(username, password):
            st.session_state.username = username
            st.success(f"Welcome back, {username}!")
            st.rerun()
        else:
            st.error("Invalid credentials")

def register_section():
    st.subheader("Register")
    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Register"):
        if register_user(new_user, new_pass):
            st.success("Registered successfully. Please login.")
        else:
            st.warning("User already exists.")

def tab1_llm_chat():
    st.subheader("Talk to AI Assistant")
    prompt = st.text_area("Enter your prompt")
    if st.button("Send Prompt"):
        if not is_safe_prompt(prompt):
            st.warning("Prompt blocked by filter.")
            return
        masked_prompt = mask_sensitive_data(prompt)
        response = requests.post("http://127.0.0.1:8000/generate", json={"prompt": masked_prompt, "user": st.session_state.username})
        if response.status_code == 200:
            reply = response.json()["response"]
            st.text_area("LLM Response", reply, height=200)
            log_audit(prompt, reply, st.session_state.username)
        else:
            st.error("LLM backend failed")

def tab2_user_chat():
    st.subheader("Send message to another user")
    recipient = st.text_input("Recipient Username")
    message = st.text_area("Message")
    if st.button("Send Message"):
        with open("user_chat_log.jsonl", "a") as f:
            f.write(json.dumps({
                "from": st.session_state.username,
                "to": recipient,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }) + "\n")
        st.success("Message sent!")

def tab3_dashboard():
    st.subheader("Usage Dashboard")

    # --- LLM Interactions ---
    st.markdown("### LLM Interactions")
    try:
        with open("audit_log.jsonl", "r") as f:
            for line in f.readlines()[-5:]:
                entry = json.loads(line)
                st.write(f"🧠 {entry['user']} → {entry['prompt']} → {entry['response']}")
    except:
        st.warning("No audit logs yet.")

    # --- User Chat Logs ---
    st.markdown("### 📥 Messages Received")
    try:
        with open("user_chat_log.jsonl", "r") as f:
            received = [
                json.loads(line)
                for line in f
                if json.loads(line)["to"] == st.session_state.username
            ]
        for msg in reversed(received[-5:]):
            st.info(f"From {msg['from']} at {msg['timestamp']}:\n\n{msg['message']}")
    except:
        st.warning("No received messages yet.")

    st.markdown("### 📤 Messages Sent")
    try:
        with open("user_chat_log.jsonl", "r") as f:
            sent = [
                json.loads(line)
                for line in f
                if json.loads(line)["from"] == st.session_state.username
            ]
        for msg in reversed(sent[-5:]):
            st.success(f"To {msg['to']} at {msg['timestamp']}:\n\n{msg['message']}")
    except:
        st.warning("No sent messages yet.")

def show_signout():
    with st.sidebar:
        st.write(f"👤 Logged in as: `{st.session_state.username}`")
        if st.button("🔒 Sign Out"):
            st.session_state.username = None
            st.rerun()

# ========== Main UI ==========
if not st.session_state.username:
    st.title("Welcome to SmartEnterprise AI Suite")
    auth_option = st.radio("Choose:", ["Login", "Register"])
    login_section() if auth_option == "Login" else register_section()
else:
    show_signout()
    tab = st.tabs(["AI Assistant", "User Chat", "Dashboard"])
    with tab[0]: tab1_llm_chat()
    with tab[1]: tab2_user_chat()
    with tab[2]: tab3_dashboard()
