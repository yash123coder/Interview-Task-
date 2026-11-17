
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models import Lead, ProcessingJob
from app.schemas.lead import LeadCreate, SalesStatus


def create_lead(db: Session, payload: LeadCreate):

    existing_lead = db.query(Lead).filter(
        or_(
            Lead.email == payload.email,
            Lead.phone == payload.phone
        )
    ).first()

    if existing_lead:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Duplicate lead detected",
                "existing_lead_id": existing_lead.id
            }
        )

    lead = Lead(**payload.model_dump())

    try:
        db.add(lead)
        db.flush()

        job = ProcessingJob(
            lead_id=lead.id,
            status="QUEUED"
        )

        db.add(job)
        db.commit()
        db.refresh(lead)

        return lead

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lead already exists"
        )

    except Exception:
        db.rollback()
        raise


def get_leads(db: Session, skip: int = 0, limit: int = 20):

    return (
        db.query(Lead)
        .order_by(Lead.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_lead_by_id(db: Session, lead_id: int):

    lead = db.query(Lead).filter(
        Lead.id == lead_id
    ).first()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    return lead


def update_lead_status(
    db: Session,
    lead_id: int,
    new_status: SalesStatus
):

    lead = get_lead_by_id(db, lead_id)

    lead.sales_status = new_status.value

    db.commit()
    db.refresh(lead)

    return lead
