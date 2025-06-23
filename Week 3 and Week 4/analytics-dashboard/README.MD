Analytics Dashboard Documentation
Overview
The Enterprise Chat Analytics Dashboard provides real-time insights into chat activity, user engagement, and message trends within the enterprise chat application. It is built with Streamlit and connects directly to the shared SQLite database used by the chat backend.

1. System Architecture
Components
Data Source:

SQLite database (shared/chat.db) containing chat messages.

Data Processing Pipeline:

Python script (Streamlit app) loads and processes data using pandas.

Visualization Layer:

Streamlit components render metrics, charts, and tables for end users.

Real-Time Monitoring:

Dashboard refreshes data every few seconds to reflect the latest activity.

Architecture Diagram
text
+-------------------+
|   SQLite Database |
|   (chat.db)       |
+---------+---------+
          |
          v
+---------+---------+
| Data Loader       |  (pandas, sqlite3)
+---------+---------+
          |
          v
+---------+---------+
| Data Processor    |  (word counts, user stats)
+---------+---------+
          |
          v
+---------+---------+
| Visualization     |  (Streamlit: charts, tables)
+-------------------+
2. Data Flow Documentation
Data Extraction:
The dashboard connects to the shared SQLite database and retrieves all messages from the messages table.

Data Processing:

Aggregates messages per user.

Counts unique users.

Extracts and counts the most common words.

Prepares data for visualizations (bar chart, pie chart, tables).

Visualization:

Displays key metrics (total messages, unique users).

Renders bar charts for user activity.

Shows top word frequencies.

Displays a pie chart of message distribution by user.

Real-Time Monitoring:

The dashboard uses a short cache timeout or periodic refresh to update metrics and charts in near real-time as new messages are added.

3. Performance Metrics
Data Load Time:

The dashboard measures and displays the time taken to load and process data from the database.

Rows Processed:

Displays the number of messages (rows) analyzed.

Refresh Interval:

Data is refreshed every few seconds (configurable), balancing real-time insights with system performance.

Resource Usage:

For larger deployments, consider monitoring CPU and memory usage (can be tracked with external tools).

Example Sidebar Metrics:

text
Data load time: 0.12s
Rows processed: 1,250
Last update: 14:32:10
4. User Guide
Accessing the Dashboard
Run the Dashboard:

Navigate to the frontend or dashboard folder.

Activate your Python environment.

Start Streamlit:

text
streamlit run analytics_dashboard.py
Open the provided local URL in your browser.

Dashboard Features:

Top Metrics:
View total messages, unique users, and the index of the last message.

Messages per User:
Bar chart showing how many messages each user has sent.

Most Common Words:
Table of the 10 most frequent words in all messages.

Message Share by User:
Pie chart visualizing the proportion of messages by user.

Live Refresh:
Enable or disable live data refresh to see updates as they happen.

Interpreting Results:

Use the metrics and charts to identify active users, trending topics, and overall chat activity.

The dashboard is updated automatically; you can also manually refresh if needed.

Troubleshooting:

If you see "No messages found," ensure the backend is running and the database contains messages.

For database errors, check that the path to chat.db is correct and accessible.

5. Extending the Dashboard
Integrate additional analytics (e.g., sentiment analysis, message trends over time).

Connect to a production database (e.g., PostgreSQL) for scalability.

Add export options for reports (CSV, PDF).

Implement user authentication for dashboard access if required.