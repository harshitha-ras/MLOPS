import streamlit as st
from data_pipeline import load_metrics
from visualizations import create_dataframe, line_chart, bar_chart, latency_chart

st.set_page_config(page_title="📊 Analytics Dashboard", layout="wide")
st.title("📈 SmartEnterprise Analytics Dashboard")

metrics = load_metrics()
df = create_dataframe(metrics)

col1, col2, col3 = st.columns(3)
col1.metric("📨 Messages (latest)", df['messages_sent'].iloc[-1])
col2.metric("👤 Users (latest)", df['active_users'].iloc[-1])
col3.metric("⚡ Latency (ms)", f"{df['avg_latency'].iloc[-1]*1000:.0f} ms")

st.plotly_chart(line_chart(df), use_container_width=True)
st.plotly_chart(bar_chart(df), use_container_width=True)
st.plotly_chart(latency_chart(df), use_container_width=True)
