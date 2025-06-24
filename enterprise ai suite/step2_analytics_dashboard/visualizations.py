import pandas as pd
import plotly.express as px

def create_dataframe(metrics):
    return pd.DataFrame(metrics)

def line_chart(df):
    return px.line(df, x="date", y="messages_sent", title="Messages Sent Per Day")

def bar_chart(df):
    return px.bar(df, x="date", y="active_users", title="Active Users Per Day")

def latency_chart(df):
    return px.area(df, x="date", y="avg_latency", title="Avg Response Latency")
