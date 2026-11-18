
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    Text,
    Index
)

from app.db.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    phone = Column(
        String(16),
        unique=True,
        index=True,
        nullable=False
    )

    company = Column(String(200), nullable=True)

    requirement = Column(Text, nullable=False)

    budget = Column(Float, nullable=True)

    source = Column(String(100), default="Website")

    sales_status = Column(
        String(30),
        default="NEW",
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False
    )


class LeadAnalysis(Base):
    __tablename__ = "lead_analysis"

    id = Column(Integer, primary_key=True, index=True)

    lead_id = Column(
        Integer,
        ForeignKey("leads.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    classification = Column(String(20), nullable=False)

    confidence = Column(Float, nullable=False)

    reasoning = Column(Text, nullable=True)

    recommended_action = Column(Text, nullable=True)

    missing_information = Column(JSON, nullable=True)

    # Retained for compatibility with existing application code.
    extracted_requirements = Column(JSON, nullable=True)

    recommended_response = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)

    lead_id = Column(
        Integer,
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False
    )

    status = Column(
        String(30),
        default="QUEUED",
        nullable=False
    )

    attempts = Column(Integer, default=0, nullable=False)

    error_message = Column(Text, nullable=True)

    next_retry_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False
    )

    __table_args__ = (
        Index("ix_jobs_status_created", "status", "created_at"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    actor = Column(String(100), nullable=False)

    action = Column(String(100), nullable=False)

    resource_type = Column(String(100), nullable=False)

    resource_id = Column(String(100), nullable=True)

    details = Column(JSON, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )
