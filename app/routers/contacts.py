# app/routers/contacts.py
from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.business_manager import BusinessManager
from app.data_provider import NotFoundError
from app.dependencies import get_business_manager
from app.models import Contact
from app.schemas import ContactSave, ContactResponse

router = APIRouter(prefix="/api/contacts", tags=["Contacts"])


def _to_response(ct: Contact) -> ContactResponse:
    return ContactResponse(
        contact_id=ct.contact_id, company_id=ct.company_id,
        full_name=ct.full_name, title=ct.title,
        email=ct.email, phone=ct.phone, linkedin=ct.linkedin,
    )


@router.get("/", response_model=List[ContactResponse], summary="Get all contacts")
def get_all_contacts(bm: BusinessManager = Depends(get_business_manager)):
    return [_to_response(ct) for ct in bm.get_all_contacts()]


@router.get("/{contact_id}", response_model=ContactResponse, summary="Get contact by ID")
def get_contact(contact_id: int, bm: BusinessManager = Depends(get_business_manager)):
    contact = bm.get_contact_by_id(contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail=f"Contact id={contact_id} not found")
    return _to_response(contact)


@router.post("/", response_model=ContactResponse,
             status_code=status.HTTP_201_CREATED, summary="Create a contact")
def create_contact(body: ContactSave, bm: BusinessManager = Depends(get_business_manager)):
    saved = bm.save_contact(
        Contact(None, body.company_id, body.full_name,
                body.title, body.email, body.phone, body.linkedin)
    )
    return _to_response(saved)


@router.put("/{contact_id}", response_model=ContactResponse, summary="Update a contact")
def update_contact(contact_id: int, body: ContactSave,
                   bm: BusinessManager = Depends(get_business_manager)):
    try:
        saved = bm.save_contact(
            Contact(contact_id, body.company_id, body.full_name,
                    body.title, body.email, body.phone, body.linkedin)
        )
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"Contact id={contact_id} not found")
    return _to_response(saved)
