
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.lead import (
    LeadCreate,
    LeadResponse,
    LeadStatusUpdate
)
from app.services.lead_service import (
    create_lead,
    get_leads,
    get_lead_by_id,
    update_lead_status
)


router = APIRouter(
    prefix="/leads",
    tags=["Leads"]
)


@router.post(
    "",
    response_model=LeadResponse,
    status_code=201
)
def create_new_lead(
    payload: LeadCreate,
    db: Session = Depends(get_db)
):
    return create_lead(db, payload)


@router.get(
    "",
    response_model=List[LeadResponse]
)
def list_leads(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return get_leads(db, skip, limit)


@router.get(
    "/{lead_id}",
    response_model=LeadResponse
)
def retrieve_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    return get_lead_by_id(db, lead_id)


@router.patch(
    "/{lead_id}/status",
    response_model=LeadResponse
)
def change_lead_status(
    lead_id: int,
    payload: LeadStatusUpdate,
    db: Session = Depends(get_db)
):
    return update_lead_status(
        db,
        lead_id,
        payload.sales_status
    )
