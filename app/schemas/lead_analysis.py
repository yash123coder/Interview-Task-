from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, ConfigDict


class LeadAssessment(BaseModel):

    classification: Literal["HOT", "WARM", "COLD"]

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    reasoning: str = Field(
        min_length=10,
        max_length=500
    )

    recommended_action: str = Field(
        min_length=5,
        max_length=300
    )

    missing_information: list[str] = Field(
        default_factory=list
    )


class LeadAnalysisResponse(BaseModel):

    id: int
    lead_id: int
    classification: str
    confidence: float
    reasoning: Optional[str] = None
    recommended_action: Optional[str] = None
    missing_information: Optional[list[str]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)