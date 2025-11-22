Chemical Equipment Parameter Visualizer (Hybrid Web + Desktop App)

A hybrid Web + Desktop application for uploading, analyzing, and visualizing chemical equipment data.
Powered by a Django REST API backend, a React.js web frontend, and a PyQt5 desktop client, all communicating through a single shared API.
 Features Overview
 Backend – Django + DRF
CSV upload (equipment details)
Data parsing using Pandas
Summary analytics:
Total equipment count
Average Flowrate / Pressure / Temperature
Equipment Type Distribution
Stores last 5 uploaded datasets
PDF report generation
Token-based authentication (DRF TokenAuth)
CORS enabled for frontend access

Web Frontend – React + Chart.js

User Login & Signup

Upload CSV file to backend

Render data table

Generate interactive charts (Bar & Pie)

View summary + previous uploads history

Download PDF report
Desktop App – PyQt5 + Matplotlib

Login & Signup UI

CSV upload functionality

Data table visualization

Matplotlib charts

Summary + history views

PDF generation support

Project Structure
chemical_visualizer_project/
│
├── backend/                 # Django REST API
│   ├── api/
│   ├── backend/settings.py
│   ├── requirements.txt
│   └── ...
│
├── frontend-web/            # React Web App
│   ├── src/
│   └── package.json
│
├── frontend-desktop/        # PyQt5 Desktop App
│   ├── app.py
│   ├── ui/
│   └── requirements.txt
│
├── sample_equipment_data.csv
└── README.md
Installation & Running Locally
Backend (Django REST API)
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
Web Frontend (React.js)
cd frontend-web
npm install
npm start
Desktop Client (PyQt5)
cd frontend-desktop
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python app.py
Authentication Guide

Both frontends require token-based authentication.

1. Signup (API)
2. POST /api/register/
{
  "username": "user",
  "password": "pass"
}
Login (Get Token)
POST /api/auth/api-token-auth/
{
  "username": "user",
  "password": "pass"
}
Response:
{ "token": "<your-token>" }
Send token with every API request:
Authorization: Token <your-token>
