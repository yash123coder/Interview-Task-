
from typing import List
from fastapi import HTTPException, status

from app.schemas.lead_analysis import LeadAnalysisResponse

from app.services.lead_classifier import (
    classify_lead,
    LeadClassificationError,
)

from app.services.lead_analysis_service import (
    save_lead_assessment,
    get_lead_assessment,
    LeadAnalysisPersistenceError,
)
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

@router.post(
    "/{lead_id}/analyze",
    response_model=LeadAnalysisResponse
)
def analyze_existing_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    # First verify that the lead exists.
    lead = get_lead_by_id(db, lead_id)

    # Prepare lead information for Ollama.
    lead_data = {
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "company": lead.company,
        "requirement": lead.requirement,
        "budget": lead.budget,
        "source": lead.source,
    }

    # Generate AI assessment.
    try:
        assessment = classify_lead(lead_data)

    except LeadClassificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc)
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc)
        )

    # Save assessment in database.
    try:
        saved_analysis = save_lead_assessment(
            db,
            lead_id,
            assessment
        )

        return saved_analysis

    except LeadAnalysisPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )


@router.get(
    "/{lead_id}/analysis",
    response_model=LeadAnalysisResponse
)
def retrieve_lead_analysis(
    lead_id: int,
    db: Session = Depends(get_db)
):
    # Verify lead exists.
    get_lead_by_id(db, lead_id)

    # Retrieve saved assessment.
    analysis = get_lead_assessment(db, lead_id)

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI assessment not found for this lead"
        )

    return analysis