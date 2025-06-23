import streamlit as st
from pathlib import Path
import sqlite3
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt


DB = Path(__file__).parents[1]/"enterprise-chat/shared/chat.db"

st.title("📊 Enterprise Chat Analytics")

@st.cache_data(ttl=3)
def load_data():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM messages", conn)
    conn.close()
    return df

df = load_data()

if df.empty:
    st.warning("No messages found.")
    st.stop()

st.markdown(f"**Total Messages:** {len(df)}")
st.markdown(f"**Unique Users:** {df['sender'].nunique()}")
st.markdown(f"**Last Message Index:** {df.index.max()}")

st.subheader("Messages per User")
msg_counts = df['sender'].value_counts()
st.bar_chart(msg_counts)

st.subheader("Most Common Words")
words = " ".join(df['message']).lower().split()
filtered = [w for w in words if w.isalpha() and len(w) > 2]
common = Counter(filtered).most_common(10)
word_df = pd.DataFrame(common, columns=["Word", "Frequency"])
st.dataframe(word_df)

st.subheader("Message Share by User")
fig, ax = plt.subplots()
ax.pie(msg_counts, labels=list(map(str, msg_counts.index)), autopct='%1.1f%%')
st.pyplot(fig)
