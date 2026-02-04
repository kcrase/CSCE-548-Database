from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Optional


class StatusType(StrEnum):
    SAVED = "SAVED"
    APPLIED = "APPLIED"
    SCREEN = "SCREEN"
    INTERVIEW = "INTERVIEW"
    ASSESSMENT = "ASSESSMENT"
    OFFER = "OFFER"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    GHOSTED = "GHOSTED"


@dataclass(slots=True)
class Company:
    company_id: Optional[int]
    name: str
    website: Optional[str] = None
    company_location: Optional[str] = None


@dataclass(slots=True)
class Contact:
    contact_id: Optional[int]
    company_id: int
    full_name: str
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None


@dataclass(slots=True)
class JobPosting:
    job_id: Optional[int]
    company_id: int
    job_title: str
    job_location: Optional[str] = None
    employment_type: Optional[str] = None
    job_url: Optional[str] = None
    salary: Optional[Decimal] = None
    posted_date: Optional[date] = None


@dataclass(slots=True)
class Application:
    application_id: Optional[int]
    job_id: int
    applied_date: Optional[date] = None
    source: Optional[str] = None
    priority: Optional[int] = None
    resume: Optional[str] = None


@dataclass(slots=True)
class ApplicationStatus:
    # Per your requirement: these are OBJECT references, not IDs.
    company: Company
    contact: Optional[Contact]
    job: JobPosting
    application: Application

    status_id: Optional[int]
    status: StatusType
