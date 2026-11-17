
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db


router = APIRouter(
    tags=["Health"]
)


@router.get("/health")
def application_health():

    return {
        "status": "healthy",
        "service": "AI Lead Management API"
    }


@router.get("/api/health/database")
def database_health(db: Session = Depends(get_db)):

    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )
