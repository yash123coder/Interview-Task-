
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import verify_hermes_api_key
from app.db.database import get_db
from app.db.models import AuditLog
from app.schemas.lead import LeadResponse, LeadStatusUpdate, SalesStatus
from app.services.lead_service import get_lead_by_id, update_lead_status


router = APIRouter(
    prefix="/internal",
    tags=["Hermes Agent"],
    dependencies=[Depends(verify_hermes_api_key)]
)


@router.get(
    "/leads/{lead_id}",
    response_model=LeadResponse
)
def lookup_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    lead = get_lead_by_id(db, lead_id)

    audit_entry = AuditLog(
        actor="hermes_agent",
        action="LOOKUP_LEAD",
        resource_type="lead",
        resource_id=str(lead_id),
        details={
            "operation": "lead_lookup",
            "result": "success"
        }
    )

    try:
        db.add(audit_entry)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return lead


@router.patch(
    "/leads/{lead_id}/status",
    response_model=LeadResponse
)
def update_agent_lead_status(
    lead_id: int,
    payload: LeadStatusUpdate,
    db: Session = Depends(get_db)
):
    # Only allow Hermes to mark a lead as CONTACTED.
    # CONVERTED and LOST require human approval.
    if payload.sales_status != SalesStatus.CONTACTED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Hermes can only set a lead to CONTACTED. "
                "CONVERTED and LOST require human approval."
            )
        )

    lead = get_lead_by_id(db, lead_id)
    previous_status = lead.sales_status

    updated_lead = update_lead_status(
        db,
        lead_id,
        payload.sales_status
    )

    audit_entry = AuditLog(
        actor="hermes_agent",
        action="UPDATE_LEAD_STATUS",
        resource_type="lead",
        resource_id=str(lead_id),
        details={
            "operation": "lead_status_update",
            "previous_status": previous_status,
            "new_status": payload.sales_status.value,
            "result": "success"
        }
    )

    try:
        db.add(audit_entry)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return updated_lead
