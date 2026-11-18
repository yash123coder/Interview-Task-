from sqlalchemy.orm import Session

from app.db.models import Lead, LeadAnalysis
from app.schemas.lead_analysis import LeadAssessment


class LeadAnalysisPersistenceError(Exception):
    """Raised when an AI assessment cannot be saved."""


def save_lead_assessment(
    db: Session,
    lead_id: int,
    assessment: LeadAssessment
) -> LeadAnalysis:

    lead = db.query(Lead).filter(
        Lead.id == lead_id
    ).first()

    if not lead:
        raise ValueError(
            f"Lead with ID {lead_id} does not exist."
        )

    try:
        analysis = db.query(LeadAnalysis).filter(
            LeadAnalysis.lead_id == lead_id
        ).first()

        if analysis is None:
            analysis = LeadAnalysis(lead_id=lead_id)
            db.add(analysis)

        analysis.classification = assessment.classification
        analysis.confidence = assessment.confidence
        analysis.reasoning = assessment.reasoning
        analysis.recommended_action = assessment.recommended_action
        analysis.missing_information = assessment.missing_information

        db.commit()
        db.refresh(analysis)

        return analysis

    except Exception as exc:
        db.rollback()

        raise LeadAnalysisPersistenceError(
            f"Unable to save lead assessment: {exc}"
        ) from exc


def get_lead_assessment(
    db: Session,
    lead_id: int
):
    return db.query(LeadAnalysis).filter(
        LeadAnalysis.lead_id == lead_id
    ).first()