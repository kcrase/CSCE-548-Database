# app/routers/job_postings.py
from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.business_manager import BusinessManager
from app.data_provider import NotFoundError
from app.dependencies import get_business_manager
from app.models import JobPosting
from app.schemas import JobPostingSave, JobPostingResponse

router = APIRouter(prefix="/api/job-postings", tags=["Job Postings"])


def _to_response(j: JobPosting) -> JobPostingResponse:
    return JobPostingResponse(
        job_id=j.job_id, company_id=j.company_id,
        job_title=j.job_title, job_location=j.job_location,
        employment_type=j.employment_type, job_url=j.job_url,
        salary=j.salary, posted_date=j.posted_date,
    )


@router.get("/", response_model=List[JobPostingResponse], summary="Get all job postings")
def get_all_job_postings(bm: BusinessManager = Depends(get_business_manager)):
    return [_to_response(j) for j in bm.get_all_job_postings()]


@router.get("/{job_id}", response_model=JobPostingResponse, summary="Get job posting by ID")
def get_job_posting(job_id: int, bm: BusinessManager = Depends(get_business_manager)):
    job = bm.get_job_posting_by_id(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"JobPosting id={job_id} not found")
    return _to_response(job)


@router.post("/", response_model=JobPostingResponse,
             status_code=status.HTTP_201_CREATED, summary="Create a job posting")
def create_job_posting(body: JobPostingSave, bm: BusinessManager = Depends(get_business_manager)):
    saved = bm.save_job_posting(
        JobPosting(None, body.company_id, body.job_title, body.job_location,
                   body.employment_type, body.job_url, body.salary, body.posted_date)
    )
    return _to_response(saved)


@router.put("/{job_id}", response_model=JobPostingResponse, summary="Update a job posting")
def update_job_posting(job_id: int, body: JobPostingSave,
                       bm: BusinessManager = Depends(get_business_manager)):
    try:
        saved = bm.save_job_posting(
            JobPosting(job_id, body.company_id, body.job_title, body.job_location,
                       body.employment_type, body.job_url, body.salary, body.posted_date)
        )
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"JobPosting id={job_id} not found")
    return _to_response(saved)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a job posting")
def delete_job_posting(job_id: int, bm: BusinessManager = Depends(get_business_manager)):
    try:
        bm.delete_job_posting(job_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"JobPosting id={job_id} not found")
