# app/routers/application_statuses.py
#
# ApplicationStatus is the most complex router because its domain object
# embeds full Company, Contact, JobPosting, and Application objects.
# The router:
#   1. Accepts flat IDs in the request body (ApplicationStatusSave).
#   2. Resolves each ID to a full domain object via BusinessManager.
#   3. Constructs the ApplicationStatus and delegates to save_application_status.
#   4. Returns the fully expanded ApplicationStatusResponse.

from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.business_manager import BusinessManager
from app.data_provider import NotFoundError
from app.dependencies import get_business_manager
from app.models import ApplicationStatus
from app.schemas import (
    ApplicationStatusSave, ApplicationStatusResponse,
    CompanyResponse, ContactResponse,
    JobPostingResponse, ApplicationResponse,
)

router = APIRouter(prefix="/api/application-statuses", tags=["Application Statuses"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _to_response(s: ApplicationStatus) -> ApplicationStatusResponse:
    contact_resp = None
    if s.contact is not None:
        contact_resp = ContactResponse(
            contact_id=s.contact.contact_id, company_id=s.contact.company_id,
            full_name=s.contact.full_name, title=s.contact.title,
            email=s.contact.email, phone=s.contact.phone, linkedin=s.contact.linkedin,
        )
    return ApplicationStatusResponse(
        status_id=s.status_id,
        status=s.status.value,
        company=CompanyResponse(
            company_id=s.company.company_id, name=s.company.name,
            website=s.company.website, company_location=s.company.company_location,
        ),
        contact=contact_resp,
        job=JobPostingResponse(
            job_id=s.job.job_id, company_id=s.job.company_id,
            job_title=s.job.job_title, job_location=s.job.job_location,
            employment_type=s.job.employment_type, job_url=s.job.job_url,
            salary=s.job.salary, posted_date=s.job.posted_date,
        ),
        application=ApplicationResponse(
            application_id=s.application.application_id, job_id=s.application.job_id,
            applied_date=s.application.applied_date, source=s.application.source,
            priority=s.application.priority, resume=s.application.resume,
        ),
    )


def _resolve(body: ApplicationStatusSave, bm: BusinessManager,
             status_id=None) -> ApplicationStatus:
    """Resolve flat IDs to full domain objects. Raises 404 for any missing ID."""
    company = bm.get_company_by_id(body.company_id)
    if company is None:
        raise HTTPException(status_code=404, detail=f"Company id={body.company_id} not found")

    contact = None
    if body.contact_id is not None:
        contact = bm.get_contact_by_id(body.contact_id)
        if contact is None:
            raise HTTPException(status_code=404, detail=f"Contact id={body.contact_id} not found")

    job = bm.get_job_posting_by_id(body.job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"JobPosting id={body.job_id} not found")

    application = bm.get_application_by_id(body.application_id)
    if application is None:
        raise HTTPException(status_code=404, detail=f"Application id={body.application_id} not found")

    return ApplicationStatus(
        company=company, contact=contact, job=job,
        application=application, status_id=status_id, status=body.status,
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[ApplicationStatusResponse],
            summary="Get all application statuses")
def get_all_statuses(bm: BusinessManager = Depends(get_business_manager)):
    """Return every application status with all nested objects expanded."""
    return [_to_response(s) for s in bm.get_all_application_statuses()]


@router.get("/{status_id}", response_model=ApplicationStatusResponse,
            summary="Get application status by ID")
def get_status(status_id: int, bm: BusinessManager = Depends(get_business_manager)):
    """Return a single application status with all nested objects, or 404."""
    s = bm.get_application_status_by_id(status_id)
    if s is None:
        raise HTTPException(status_code=404, detail=f"ApplicationStatus id={status_id} not found")
    return _to_response(s)


@router.post("/", response_model=ApplicationStatusResponse,
             status_code=status.HTTP_201_CREATED, summary="Create an application status")
def create_status(body: ApplicationStatusSave,
                  bm: BusinessManager = Depends(get_business_manager)):
    """
    Create a new application status. Supply flat IDs — the API resolves them
    to full objects automatically. contact_id is optional.
    """
    app_status = _resolve(body, bm, status_id=None)
    saved = bm.save_application_status(app_status)
    return _to_response(saved)


@router.put("/{status_id}", response_model=ApplicationStatusResponse,
            summary="Update an application status")
def update_status(status_id: int, body: ApplicationStatusSave,
                  bm: BusinessManager = Depends(get_business_manager)):
    """
    Update an existing application status. Most common use: advance the
    status value (e.g. SAVED → APPLIED → INTERVIEW). Returns 404 if not found.
    """
    try:
        app_status = _resolve(body, bm, status_id=status_id)
        saved = bm.save_application_status(app_status)
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"ApplicationStatus id={status_id} not found")
    return _to_response(saved)


@router.delete("/{status_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete an application status")
def delete_status(status_id: int, bm: BusinessManager = Depends(get_business_manager)):
    try:
        bm.delete_application_status(status_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"ApplicationStatus id={status_id} not found")
