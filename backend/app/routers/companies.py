# app/routers/companies.py
from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.business_manager import BusinessManager
from app.data_provider import NotFoundError
from app.dependencies import get_business_manager
from app.models import Company
from app.schemas import CompanySave, CompanyResponse

router = APIRouter(prefix="/api/companies", tags=["Companies"])


def _to_response(c: Company) -> CompanyResponse:
    return CompanyResponse(
        company_id=c.company_id, name=c.name,
        website=c.website, company_location=c.company_location,
    )


@router.get("/", response_model=List[CompanyResponse], summary="Get all companies")
def get_all_companies(bm: BusinessManager = Depends(get_business_manager)):
    return [_to_response(c) for c in bm.get_all_companies()]


@router.get("/{company_id}", response_model=CompanyResponse, summary="Get company by ID")
def get_company(company_id: int, bm: BusinessManager = Depends(get_business_manager)):
    company = bm.get_company_by_id(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail=f"Company id={company_id} not found")
    return _to_response(company)


@router.post("/", response_model=CompanyResponse,
             status_code=status.HTTP_201_CREATED, summary="Create a company")
def create_company(body: CompanySave, bm: BusinessManager = Depends(get_business_manager)):
    saved = bm.save_company(Company(None, body.name, body.website, body.company_location))
    return _to_response(saved)


@router.put("/{company_id}", response_model=CompanyResponse, summary="Update a company")
def update_company(company_id: int, body: CompanySave,
                   bm: BusinessManager = Depends(get_business_manager)):
    try:
        saved = bm.save_company(Company(company_id, body.name, body.website, body.company_location))
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"Company id={company_id} not found")
    return _to_response(saved)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a company")
def delete_company(company_id: int, bm: BusinessManager = Depends(get_business_manager)):
    try:
        bm.delete_company(company_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"Company id={company_id} not found")
