# Job Tracker

A full-stack n-tier job application tracker built for CSCE 548 — Database Systems at the University of South Carolina.

Track your job applications, companies, contacts, job postings, and pipeline statuses through a clean web interface backed by a REST API and MySQL database.

---

## Architecture

```
Browser (React + Vite)
    ↓  HTTP / JSON
FastAPI REST API (Uvicorn)      ← Service Layer
    ↓
BusinessManager (Python)        ← Business Layer
    ↓
DataProvider (Python)           ← Data Layer
    ↓
MySQL 8.0
```

---

## Project Structure

```
CSCE-548-Database/
├── README.md
├── .gitignore
├── pyrightconfig.json
├── backend/                    ← Python FastAPI application
│   ├── main.py                 ← FastAPI entry point (run this with uvicorn)
│   ├── demo.py                 ← Layer testing script (data / business / service)
│   ├── pytest.ini
│   ├── requirements.txt
│   ├── schema.sql              ← Creates the database tables
│   ├── seed.sql                ← Inserts sample data
│   ├── app/
│   │   ├── models.py           ← Domain objects (Company, Contact, JobPosting, etc.)
│   │   ├── data_provider.py    ← Data layer — raw MySQL queries
│   │   ├── business_manager.py ← Business layer — save/delete/get logic
│   │   ├── schemas.py          ← Pydantic request/response models
│   │   ├── dependencies.py     ← FastAPI dependency injection
│   │   └── routers/            ← Service layer — one controller per domain object
│   │       ├── companies.py
│   │       ├── contacts.py
│   │       ├── job_postings.py
│   │       ├── applications.py
│   │       └── application_statuses.py
│   └── tests/
│       └── test_core.py        ← Pytest CRUD tests
└── frontend/                   ← React + Vite application
    ├── index.html
    ├── package.json
    ├── vite.config.js          ← Proxies /api → localhost:8000
    └── src/
        ├── api/client.js       ← All FastAPI endpoint calls
        ├── components/         ← Navbar, Modal, Toast, StatusBadge
        └── pages/              ← Dashboard, Pipeline, Applications, etc.
```

---

## Prerequisites

| Software | Version | Link |
|---|---|---|
| Python | 3.11+ | [python.org](https://python.org/downloads) |
| Node.js | 18 LTS+ | [nodejs.org](https://nodejs.org) |
| MySQL | 8.0+ | [dev.mysql.com](https://dev.mysql.com/downloads) |
| Git | Any | [git-scm.com](https://git-scm.com) |

> **Windows:** During Python installation, check **Add Python to PATH**.

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/kcrasborn/CSCE-548-Database.git
cd CSCE-548-Database
```

### 2. Set up the database

```bash
mysql -u root -p < backend/schema.sql
mysql -u root -p job_tracker < backend/seed.sql
```

### 3. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
```

---

## Running the Project

Three things must run simultaneously — MySQL as a background service, plus one terminal each for the backend and frontend.

**Terminal 1 — Backend:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Then open **http://localhost:3000** in your browser.

---

## Environment Variables

The backend reads database credentials from environment variables. Defaults are set for the development environment — override if your MySQL uses different credentials.

**PowerShell:**
```powershell
$env:DB_HOST     = "localhost"
$env:DB_USER     = "root"
$env:DB_PASSWORD = "your_password"
$env:DB_NAME     = "job_tracker"
$env:DB_PORT     = "3306"
```

**Command Prompt:**
```cmd
set DB_HOST=localhost
set DB_USER=root
set DB_PASSWORD=your_password
set DB_NAME=job_tracker
set DB_PORT=3306
```

---

## API Endpoints

Interactive API docs available at **http://localhost:8000/docs** when the backend is running.

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/companies | Get all companies |
| GET | /api/companies/{id} | Get by ID |
| POST | /api/companies | Create |
| PUT | /api/companies/{id} | Update |
| DELETE | /api/companies/{id} | Delete |
| GET | /api/contacts | Get all contacts |
| GET | /api/job-postings | Get all job postings |
| GET | /api/applications | Get all applications |
| GET | /api/application-statuses | Get all statuses (nested objects expanded) |

All controllers follow the same GET / GET by ID / POST / PUT / DELETE pattern.

---

## Testing

### Run demo.py (tests all three layers)

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

### Run Pytest

```powershell
$env:LAYER = "business"
pytest -v
```

---

## Domain Objects

| Object | Key Fields |
|---|---|
| Company | company_id, name, website, company_location |
| Contact | contact_id, company_id, full_name, title, email, phone, linkedin |
| JobPosting | job_id, company_id, job_title, job_location, employment_type, job_url, salary, posted_date |
| Application | application_id, job_id, applied_date, source, priority, resume |
| ApplicationStatus | status_id, company, contact, job, application, status |

**Status values:** `SAVED` → `APPLIED` → `SCREEN` → `INTERVIEW` → `ASSESSMENT` → `OFFER` → `ACCEPTED` / `REJECTED` / `WITHDRAWN` / `GHOSTED`

---

## Resetting Sample Data

To wipe all records and restore the original seed data:

```bash
mysql -u root -p job_tracker < backend/seed.sql
```

---

## Deployment Document

See `JobTracker_Deployment.pdf` in the repository root for full step-by-step deployment instructions, troubleshooting, and system test documentation.