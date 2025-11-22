Chemical Equipment Parameter Visualizer (Hybrid Web + Desktop App)

A hybrid Web + Desktop application for visualizing and analyzing chemical equipment parameters.
The system is powered by a Django REST API backend, a React.js web frontend, and a PyQt5 desktop client, all consuming the same API.

 Features
Backend (Django + DRF)

Upload CSV files containing:

Equipment Name

Type

Flowrate

Pressure

Temperature

Parse data using Pandas

Compute:

Total equipment count

Average flowrate, pressure, temperature

Equipment type distribution

Store last 5 uploaded datasets in SQLite

Provide summary APIs for frontend and desktop

Generate downloadable PDF reports

Token-based authentication (DRF TokenAuth)

CORS-enabled for web usage

 Web Frontend (React + Chart.js)

CSV upload form

Displays parsed table

Auto-generated charts (bar/pie) with Chart.js

Login & Signup (token stored locally)

View summary and history of last 5 uploads

 Desktop Frontend (PyQt5 + Matplotlib)

Login & Signup

Upload CSV directly to backend

Display processed table

Generate charts using Matplotlib

See summaries and history

 Project Structure
chemical_visualizer_project/
│
├── backend/               # Django REST API
│   ├── api/
│   ├── backend/settings.py
│   ├── requirements.txt
│   └── ...
│
├── frontend-web/          # React web app
│   ├── src/
│   └── package.json
│
├── frontend-desktop/      # PyQt5 desktop client
│   ├── app.py
│   ├── ui/
│   └── requirements.txt
│
├── sample_equipment_data.csv
└── README.md

⚙️ Installation Instructions
1️ Backend (Django REST API)
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver


Backend runs at:

➡ http://127.0.0.1:8000/api/

2️ Web Frontend (React.js)
cd frontend-web
npm install
npm start


Frontend runs at:

➡ http://localhost:3000

3️ Desktop Client (PyQt5)
cd frontend-desktop
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python app.py

 Authentication (Required for all clients)
Signup (API)
POST /api/register/
{ "username": "user", "password": "pass" }

Login (API) – Get Token
POST /api/auth/api-token-auth/
{ "username": "user", "password": "pass" }


Response:

{ "token": "<your-token>" }


Use this token in:

Authorization: Token <your-token>


Both web and desktop apps automatically store & reuse this token.
