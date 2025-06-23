import streamlit as st
import requests

API = "http://127.0.0.1:8000"

st.title("Enterprise Chat App")

if "token" not in st.session_state:
    st.subheader("Login")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        res = requests.post(f"{API}/login", json={"username": user, "password": pw})
        if res.status_code == 200:
            st.session_state.token = res.json()["access_token"]
            st.success("Logged in!")
        else:
            st.error("Invalid login")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}
st.subheader("Chat")
user_msg = st.text_input("You:")
if st.button("Send") and user_msg:
    r = requests.post(f"{API}/send", json={"sender": "admin", "message": user_msg}, headers=headers)
    if r.ok:
        st.success(r.json()["reply"])
    else:
        st.error("Error sending message")

if st.button("Refresh Messages"):
    r = requests.get(f"{API}/messages", headers=headers)
    if r.ok:
        for m in r.json():
            st.markdown(f"**{m['sender']}**: {m['message']}")
