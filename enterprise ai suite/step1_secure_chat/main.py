import streamlit as st
from auth import register_user, authenticate_user, decode_token
from chat import send_message, get_messages_for_user
from audit import log_event

st.set_page_config(page_title="Secure Chat App", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None

st.title("🛡️ Secure Enterprise Chat")

# Sidebar: Login/Register
with st.sidebar:
    st.header("🔐 Login / Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if register_user(username, password):
            st.success("Registered! Please login.")
        else:
            st.error("Username already taken.")

    if st.button("Login"):
        token = authenticate_user(username, password)
        if token:
            st.session_state.token = token
            st.success("Login successful.")
        else:
            st.error("Invalid credentials.")

# Main UI: Chat
user = decode_token(st.session_state.token) if st.session_state.token else None

if user:
    st.success(f"Logged in as: {user}")
    receiver = st.text_input("Send To (Username)")
    message = st.text_area("Message")
    if st.button("Send"):
        send_message(user, receiver, message)
        log_event(user, receiver, message)
        st.info("Message sent.")
    
    st.subheader("📨 Your Messages")
    messages = get_messages_for_user(user)
    for msg in messages:
        st.markdown(f"**{msg.sender}** at {msg.timestamp}: {msg.content}")
