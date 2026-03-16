# Job Tracker API — Setup & Hosting Guide

## Project Structure

```
project/
├── main.py                        ← FastAPI app + router registration
├── schemas.py                     ← Pydantic request / response models
├── dependencies.py                ← Shared BusinessManager (DI singleton)
├── models.py                      ← Domain objects (existing)
├── data_provider.py               ← Data access layer (existing)
├── business_manager.py            ← Business layer (existing)
├── routers/
│   ├── companies.py               ← /api/companies
│   ├── contacts.py                ← /api/contacts
│   ├── job_postings.py            ← /api/job-postings
│   ├── applications.py            ← /api/applications
│   └── application_statuses.py   ← /api/application-statuses
├── api_demo.py                    ← End-to-end API test script
└── requirements.txt
```

---

## Layer Architecture

```
HTTP Request
     │
     ▼
 FastAPI Router (Controller)   ← schemas.py validates input / output
     │
     ▼
 BusinessManager (Business Layer)
     │
     ▼
 DataProvider (Data Layer)
     │
     ▼
 MySQL Database
```

---

## 1. Prerequisites

- Python 3.11+ installed on Windows
- MySQL 8.0 running locally (or accessible remotely)
- Database seeded via `seed.sql`

Check Python version:
```
python --version
```

---

## 2. Install Dependencies

Open a terminal in your project folder and run:

```bash
pip install -r requirements.txt
```

This installs: `fastapi`, `uvicorn`, `pydantic`, `mysql-connector-python`, `requests`.

---

## 3. Configure Database Credentials

The API reads connection settings from environment variables. The defaults
match the project settings, but you can override them:

**Windows Command Prompt:**
```cmd
set DB_HOST=localhost
set DB_USER=root
set DB_PASSWORD=KeitC4658!
set DB_NAME=job_tracker
set DB_PORT=3306
```

**Windows PowerShell:**
```powershell
$env:DB_HOST     = "localhost"
$env:DB_USER     = "root"
$env:DB_PASSWORD = "KeitC4658!"
$env:DB_NAME     = "job_tracker"
$env:DB_PORT     = "3306"
```

Or edit the defaults directly in `dependencies.py` if you prefer.

---

## 4. Run the API (Development)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- `--reload` — auto-restarts when you save a file (development only)
- `--host 0.0.0.0` — makes the API reachable from other devices on your network
- `--port 8000` — change if 8000 is taken

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

---

## 5. Interactive API Docs

With the server running, open either URL in your browser:

| URL | Tool |
|-----|------|
| http://localhost:8000/docs | **Swagger UI** — click "Try it out" to test any endpoint |
| http://localhost:8000/redoc | ReDoc — clean reference docs |
| http://localhost:8000/ | Health check |

---

## 6. API Endpoints Reference

### Companies
| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/companies | Get all companies |
| GET | /api/companies/{id} | Get company by ID |
| POST | /api/companies | Create company |
| PUT | /api/companies/{id} | Update company |

### Contacts
| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/contacts | Get all contacts |
| GET | /api/contacts/{id} | Get contact by ID |
| POST | /api/contacts | Create contact |
| PUT | /api/contacts/{id} | Update contact |

### Job Postings
| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/job-postings | Get all job postings |
| GET | /api/job-postings/{id} | Get job posting by ID |
| POST | /api/job-postings | Create job posting |
| PUT | /api/job-postings/{id} | Update job posting |

### Applications
| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/applications | Get all applications |
| GET | /api/applications/{id} | Get application by ID |
| POST | /api/applications | Create application |
| PUT | /api/applications/{id} | Update application |

### Application Statuses
| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/application-statuses | Get all (nested objects expanded) |
| GET | /api/application-statuses/{id} | Get by ID (nested objects expanded) |
| POST | /api/application-statuses | Create — supply flat IDs |
| PUT | /api/application-statuses/{id} | Update (e.g. advance status) |

**ApplicationStatus request body** (flat IDs):
```json
{
  "company_id": 1,
  "contact_id": 2,
  "job_id": 3,
  "application_id": 4,
  "status": "INTERVIEW"
}
```
`contact_id` is optional (set to `null` if no contact).

**Valid status values:** `SAVED`, `APPLIED`, `SCREEN`, `INTERVIEW`,
`ASSESSMENT`, `OFFER`, `ACCEPTED`, `REJECTED`, `WITHDRAWN`, `GHOSTED`

---

## 7. Run the Automated Test Script

With the server running in one terminal, open another terminal and run:

```bash
python api_demo.py
```

Optional — if the API is on a different host or port:
```bash
python api_demo.py --base-url http://192.168.1.50:8000
```

The script will:
- Create a Company, Contact, JobPosting, Application, and ApplicationStatus
- Read each back by ID and verify fields
- Update each and verify the change persisted
- Call GetAll on every controller and show the count
- Verify that a 404 is returned for a non-existent record

All records are tagged `[TEST] API ...` with a timestamp so they are easy
to identify in the database.

---

## 8. Host on Windows Laptop (Persistent / Background)

For a server that survives terminal closures and restarts, use one of the
following approaches:

---

### Option A — NSSM (Recommended for Windows, Free)

NSSM (Non-Sucking Service Manager) wraps any executable as a Windows Service.

1. Download NSSM from https://nssm.cc/download (no install needed, just unzip)

2. Open an **Administrator** command prompt and run:
   ```cmd
   nssm install JobTrackerAPI
   ```

3. In the GUI that appears, fill in:
   - **Path:** `C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts\uvicorn.exe`
   - **Startup directory:** `C:\path\to\your\project`
   - **Arguments:** `main:app --host 0.0.0.0 --port 8000`

4. On the **Environment** tab, add your DB env vars:
   ```
   DB_PASSWORD=KeitC4658!
   DB_NAME=job_tracker
   ```

5. Click **Install service**, then start it:
   ```cmd
   nssm start JobTrackerAPI
   ```

6. The API will now auto-start with Windows.  To stop it:
   ```cmd
   nssm stop JobTrackerAPI
   ```

---

### Option B — Windows Task Scheduler (Built-in, No Install)

1. Create a `start_api.bat` file in your project folder:
   ```bat
   @echo off
   set DB_PASSWORD=KeitC4658!
   set DB_NAME=job_tracker
   cd /d C:\path\to\your\project
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. Open **Task Scheduler** → Create Basic Task
3. Set trigger: **At log on** (or **At startup**)
4. Set action: **Start a program** → Browse to `start_api.bat`
5. Check **"Run whether user is logged on or not"** for background execution

---

### Option C — Run in a Terminal (Quickest for demos)

Just run the uvicorn command and leave the terminal open.  This is the
simplest approach for screenshots and in-class demos:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 9. Access from Other Devices on the Same Network

1. Find your Windows IP address:
   ```cmd
   ipconfig
   ```
   Look for **IPv4 Address** under your active adapter (e.g. `192.168.1.42`).

2. Make sure Windows Firewall allows port 8000:
   - Open **Windows Defender Firewall** → Advanced Settings
   - New Inbound Rule → Port → TCP → 8000 → Allow

3. Other devices on the same network can now reach:
   ```
   http://192.168.1.42:8000/docs
   ```

---

## 10. Quick Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: fastapi` | Run `pip install -r requirements.txt` |
| `Address already in use` | Change `--port 8000` to another port, or kill the process using port 8000 |
| Database connection refused | Ensure MySQL is running and credentials in `dependencies.py` are correct |
| 422 Unprocessable Entity | Check request body matches the schema — use `/docs` to see required fields |
| 404 on ApplicationStatus create | Verify the company_id, job_id, and application_id all exist first |
