# Chemical Equipment Parameter Visualizer (Hybrid Web + Desktop App)

This is a **starter** complete project for the FOSSEE Winter Internship screening task: a hybrid application (Web + Desktop) backed by a Django REST API. It includes starter code for backend, React web frontend, and PyQt5 desktop client. Use this repo as a solid and well-documented foundation to finish, polish, and demo for the internship.
##  Watch Demo Video

[![Watch the video](https://img.youtube.com/vi/VQSaEJVS4Pk/0.jpg)](https://youtu.be/VQSaEJVS4Pk)

> Click the thumbnail above to watch the demo on YouTube.

## What is included
- `backend/` — Django project with Django REST Framework endpoints:
  - Upload CSV (stores file + computes summary)
  - List last 5 uploads with summaries
  - Retrieve single upload summary
  - Generate simple PDF report (endpoint)
- `frontend-web/` — React skeleton that uploads CSV, shows table and Chart.js chart
- `frontend-desktop/` — PyQt5 app that uploads CSV and displays Matplotlib charts
- `sample_equipment_data.csv` — sample data for demo
- `demo_instructions.txt` — how to run locally
- `chemical_visualizer_project.zip` — this archive (you are currently viewing files inside)


## Quick run (development)
### Backend (Django)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # on Windows use `.venv\Scripts\activate`
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```
API root: http://127.0.0.1:8000/api/

### Web Frontend (React)
```bash
cd frontend-web
npm install
npm start
# open http://localhost:3000
```
### Desktop Frontend (PyQt5)
```bash
cd frontend-desktop
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
## Backend authentication
To call the API endpoints you must create a user and obtain a token (DRF TokenAuth).
Create a user: `python manage.py createsuperuser` then obtain token by POSTing to `/api/auth/token/login/` or use DRF authtoken endpoint.

## Authentication & token retrieval (required)
This hardened project requires DRF Token Authentication for API calls. Steps:
1. Create a user (recommended: superuser) for testing:
   ```bash
   cd backend
   python manage.py createsuperuser
   ```
2. Obtain a token by POSTing credentials to the token endpoint:
   - **Endpoint:** `POST http://127.0.0.1:8000/api/auth/api-token-auth/`
   - **Body (JSON):** `{"username": "youruser", "password": "yourpass"}`
   - **Response:** `{"token": "<your-token>"}`
3. The React frontend shows a login screen. Enter username/password to obtain and store the token locally.
4. The PyQt5 desktop app includes a login row — enter credentials to fetch the token before uploading files.

Notes:
- When running frontend and backend on different hosts/ports, you may need to enable CORS in Django (install `django-cors-headers`) and allow `http://localhost:3000`.


## CORS & Running React dev server
If you run the React dev server on http://localhost:3000 it will be allowed by default in this project. If you change origin, update `CORS_ALLOWED_ORIGINS` in `backend/backend/settings.py` or set `CORS_ALLOW_ALL_ORIGINS = True` for quick testing (not recommended for production).

## API Registration (signup)
You can create a user via the API using the `/api/register/` endpoint. It returns a token which both frontends use automatically.

- Signup endpoint: `POST http://127.0.0.1:8000/api/register/` with JSON `{ "username": "user", "password": "pass" }`
- Login endpoint: `POST http://127.0.0.1:8000/api/auth/api-token-auth/` with JSON `{ "username": "user", "password": "pass" }` returns `{"token":"..."}`

The React UI provides signup and login flows. The desktop app also allows signup/login.
