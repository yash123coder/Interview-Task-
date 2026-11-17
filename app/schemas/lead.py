
import re

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator
)


class SalesStatus(str, Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    CONVERTED = "CONVERTED"
    LOST = "LOST"


class LeadCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)

    email: EmailStr

    phone: str = Field(min_length=10, max_length=16)

    company: Optional[str] = Field(
        default=None,
        max_length=200
    )

    requirement: str = Field(
        min_length=5,
        max_length=5000
    )

    budget: Optional[float] = Field(
        default=None,
        ge=0
    )

    source: str = Field(
        default="Website",
        max_length=100
    )

    @field_validator("name", "requirement", "source")
    @classmethod
    def strip_text(cls, value):
        return value.strip()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return str(value).strip().lower()

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value):
        normalized = re.sub(r"[\s()-]", "", value)

        if not re.fullmatch(r"\+?[0-9]{10,15}", normalized):
            raise ValueError("Enter a valid phone number")

        return normalized


class LeadResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    company: Optional[str]
    requirement: str
    budget: Optional[float]
    source: str
    sales_status: SalesStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadStatusUpdate(BaseModel):
    sales_status: SalesStatus
