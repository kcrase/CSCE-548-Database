# CSCE-548-Database — Job Tracker

A full-stack job application tracker built for CSCE 548.

## Project Structure

```
CSCE-548-Database/
├── backend/    ← Python FastAPI REST API (data, business, service layers)
└── frontend/   ← React web application
```

---

## Stack

| Layer | Technology |
|---|---|
| Database | MySQL 8.0 |
| Data Layer | Python — DataProvider |
| Business Layer | Python — BusinessManager |
| Service Layer | Python — FastAPI + Uvicorn |
| Frontend | React + Vite |

---

## Running the Project

Three things must be running at the same time.

### 1. MySQL
Make sure MySQL is running locally on port 3306.
Seed the database once:
```bash
mysql -u root -p job_tracker < backend/seed.sql
```

### 2. Backend API
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
API docs available at: http://localhost:8000/docs

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```
App available at: http://localhost:3000

---

## Testing the Layers

From inside the `backend/` folder:

```powershell
# Data layer
$env:LAYER = "data"
python demo.py

# Business layer
$env:LAYER = "business"
python demo.py

# Service layer (requires uvicorn running)
$env:LAYER = "service"
python demo.py
```

## Running Pytest

```bash
cd backend

# Business layer
$env:LAYER = "business"
pytest -v

# Data layer
$env:LAYER = "data"
pytest -v
```
