# app/routers/applications.py
from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.business_manager import BusinessManager
from app.data_provider import NotFoundError
from app.dependencies import get_business_manager
from app.models import Application
from app.schemas import ApplicationSave, ApplicationResponse

router = APIRouter(prefix="/api/applications", tags=["Applications"])


def _to_response(a: Application) -> ApplicationResponse:
    return ApplicationResponse(
        application_id=a.application_id, job_id=a.job_id,
        applied_date=a.applied_date, source=a.source,
        priority=a.priority, resume=a.resume,
    )


@router.get("/", response_model=List[ApplicationResponse], summary="Get all applications")
def get_all_applications(bm: BusinessManager = Depends(get_business_manager)):
    return [_to_response(a) for a in bm.get_all_applications()]


@router.get("/{application_id}", response_model=ApplicationResponse, summary="Get application by ID")
def get_application(application_id: int, bm: BusinessManager = Depends(get_business_manager)):
    app = bm.get_application_by_id(application_id)
    if app is None:
        raise HTTPException(status_code=404, detail=f"Application id={application_id} not found")
    return _to_response(app)


@router.post("/", response_model=ApplicationResponse,
             status_code=status.HTTP_201_CREATED, summary="Create an application")
def create_application(body: ApplicationSave, bm: BusinessManager = Depends(get_business_manager)):
    saved = bm.save_application(
        Application(None, body.job_id, body.applied_date,
                    body.source, body.priority, body.resume)
    )
    return _to_response(saved)


@router.put("/{application_id}", response_model=ApplicationResponse, summary="Update an application")
def update_application(application_id: int, body: ApplicationSave,
                       bm: BusinessManager = Depends(get_business_manager)):
    try:
        saved = bm.save_application(
            Application(application_id, body.job_id, body.applied_date,
                        body.source, body.priority, body.resume)
        )
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"Application id={application_id} not found")
    return _to_response(saved)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an application")
def delete_application(application_id: int, bm: BusinessManager = Depends(get_business_manager)):
    try:
        bm.delete_application(application_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"Application id={application_id} not found")
