Enterprise Chat Application
A secure, enterprise-grade chat platform built with FastAPI (backend) and Streamlit (frontend).
This project demonstrates best practices in authentication, audit logging, deployment, and security for enterprise environments.

Features
Secure Chat Interface: Real-time chat for authenticated users.

User Authentication: JWT-based, with bcrypt password hashing.

Audit Logging: All critical actions (login, message send, etc.) are logged.

Token Revocation: Admins can revoke JWT tokens.

Environment-based Secrets: All secrets and sensitive paths are managed via environment variables.

Cross-platform: Runs on Windows, Linux, or Mac.

Project Structure
text
enterprise-chat/
│
├── backend/
│   ├── main.py         # FastAPI backend
│   ├── db.py           # Database and audit log logic
│   ├── auth.py         # Authentication and security
│   └── ...             # Other backend modules
│
├── frontend/
│   ├── app.py          # Streamlit frontend
│   └── ...             # Other frontend assets
│
├── shared/
│   └── chat.db         # SQLite database (auto-created)
│
├── .env                # Environment variables (not committed)
├── requirements.txt    # Python dependencies
└── README.md           # This documentation
Prerequisites
Python 3.9 or newer

Git

Setup Instructions
1. Clone the Repository
bash
git clone <your-repo-url>
cd enterprise-chat
2. Set Up Environment Variables
Create a .env file in the root directory with the following (edit as needed):

text
JWT_SECRET=your_very_secure_secret
DB_PATH=shared/chat.db
JWT_ALGO=HS256
3. Install Dependencies
Create a virtual environment and install dependencies:

bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
Running the Application
You must run the frontend and backend from their respective folders in separate terminals.

Backend (FastAPI)
bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
The backend API will be available at http://localhost:8000

API docs: http://localhost:8000/docs

Frontend (Streamlit)
Open a new terminal:

bash
cd frontend
streamlit run app.py --server.port 8501
The chat UI will be available at http://localhost:8501

Security Documentation
Secrets: All secrets (JWT secret, DB path) are loaded from .env and never hardcoded.

Password Hashing: User passwords are stored as bcrypt hashes.

Audit Logging: All logins, message sends, edits, and deletions are recorded in the audit_log table.

Token Revocation: JWT tokens can be revoked and are checked on every request.

CORS: Backend is configured to allow cross-origin requests from the frontend.

Deployment Guide
Production Servers: Use Uvicorn for the backend. For Linux, you may use Gunicorn with the Uvicorn worker.

Reverse Proxy: For HTTPS, run both services behind Nginx or Caddy.

Environment Variables: Set all secrets and paths via .env or your hosting provider’s configuration.

Database: For production, consider migrating from SQLite to PostgreSQL or another robust RDBMS.

Process Management: Use systemd, supervisor, or similar tools to keep services running.

Performance Analysis
Concurrency: FastAPI with Uvicorn supports async requests and multiple workers.

Bottlenecks: SQLite is suitable for small teams; for higher concurrency, use PostgreSQL.

Monitoring: Use built-in logs or integrate with Prometheus/Grafana for advanced monitoring.

Troubleshooting
Database Errors: Ensure the shared directory exists and is writable.

CORS Issues: Make sure backend allows requests from the frontend origin.

Port Conflicts: Ensure ports 8000 (backend) and 8501 (frontend) are free.

Windows Users: Use Uvicorn, not Gunicorn or Waitress, for backend.

License
MIT License