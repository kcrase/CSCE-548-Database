# main.py
# FastAPI application entry point.
# Stays at the project root so uvicorn can find it easily.
#
# Run (development):
#   uvicorn main:app --reload --host 0.0.0.0 --port 8000
#
# Interactive docs (once running):
#   http://localhost:8000/docs      <- Swagger UI
#   http://localhost:8000/redoc     <- ReDoc

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import companies, contacts, job_postings, applications, application_statuses

app = FastAPI(
    title="Job Tracker API",
    description=(
        "REST API for the Job Tracker application.\n\n"
        "Each controller exposes **GET** (by ID), **GET ALL**, **POST** (create), "
        "and **PUT** (update) endpoints.\n\n"
        "ApplicationStatus responses include fully expanded nested objects "
        "(Company, Contact, JobPosting, Application) in a single round-trip."
    ),
    version="1.0.0",
)

# Allow all origins during development — tighten this in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers (one per domain object) ──────────────────────────────────
app.include_router(companies.router)
app.include_router(contacts.router)
app.include_router(job_postings.router)
app.include_router(applications.router)
app.include_router(application_statuses.router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"], summary="Health check")
def root():
    return {"status": "ok", "message": "Job Tracker API is running"}
