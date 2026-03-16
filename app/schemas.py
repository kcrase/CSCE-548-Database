# app/schemas.py
# Pydantic request and response models for the Job Tracker API.
#
# *Save    models — what the API accepts in the request body.
# *Response models — what the API returns as JSON.

from __future__ import annotations
from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
from app.models import StatusType


# ── Company ───────────────────────────────────────────────────────────────────

class CompanySave(BaseModel):
    name: str
    website: Optional[str] = None
    company_location: Optional[str] = None


class CompanyResponse(BaseModel):
    company_id: int
    name: str
    website: Optional[str] = None
    company_location: Optional[str] = None


# ── Contact ───────────────────────────────────────────────────────────────────

class ContactSave(BaseModel):
    company_id: int
    full_name: str
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None


class ContactResponse(BaseModel):
    contact_id: int
    company_id: int
    full_name: str
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None


# ── JobPosting ────────────────────────────────────────────────────────────────

class JobPostingSave(BaseModel):
    company_id: int
    job_title: str
    job_location: Optional[str] = None
    employment_type: Optional[str] = None
    job_url: Optional[str] = None
    salary: Optional[Decimal] = None
    posted_date: Optional[date] = None


class JobPostingResponse(BaseModel):
    job_id: int
    company_id: int
    job_title: str
    job_location: Optional[str] = None
    employment_type: Optional[str] = None
    job_url: Optional[str] = None
    salary: Optional[Decimal] = None
    posted_date: Optional[date] = None


# ── Application ───────────────────────────────────────────────────────────────

class ApplicationSave(BaseModel):
    job_id: int
    applied_date: Optional[date] = None
    source: Optional[str] = None
    priority: Optional[int] = None
    resume: Optional[str] = None


class ApplicationResponse(BaseModel):
    application_id: int
    job_id: int
    applied_date: Optional[date] = None
    source: Optional[str] = None
    priority: Optional[int] = None
    resume: Optional[str] = None


# ── ApplicationStatus ─────────────────────────────────────────────────────────

class ApplicationStatusSave(BaseModel):
    """Flat IDs only — the router resolves each to a full domain object."""
    company_id: int
    contact_id: Optional[int] = None
    job_id: int
    application_id: int
    status: StatusType


class ApplicationStatusResponse(BaseModel):
    """Fully expanded — all nested objects included in one response."""
    status_id: int
    status: str
    company: CompanyResponse
    contact: Optional[ContactResponse] = None
    job: JobPostingResponse
    application: ApplicationResponse
