"""Pydantic schemas for Educator and Administrator identity, access, and assignments.

Conforms to Specification v3.0 Sections 11.0, 19.1-19.6.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class EducatorRegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(..., description="Educator email address")
    password: str = Field(..., min_length=8, description="Password (at least 8 characters)")
    display_name: str = Field(..., min_length=1, max_length=255, description="Full display name")

    @field_validator("email")
    @classmethod
    def validate_and_normalize_email(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if "@" not in cleaned or "." not in cleaned.split("@")[-1]:
            raise ValueError("Invalid email format")
        return cleaned

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Display name cannot be blank")
        return cleaned


class EducatorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    display_name: str
    status: str
    created_at: datetime


class EducatorProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    display_name: str
    status: str
    created_at: datetime
    approved_at: Optional[datetime] = None


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    expires_in_minutes: int


class AssignmentCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    class_id: str
    section_id: Optional[str] = None


class AssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    educator_id: str
    class_id: str
    section_id: Optional[str] = None
    active: bool
    created_at: datetime
    revoked_at: Optional[datetime] = None


class EducatorAssignmentDetail(BaseModel):
    id: str
    class_id: str
    class_name: str
    class_code: str
    section_id: Optional[str] = None
    section_name: Optional[str] = None
    section_code: Optional[str] = None
    active: bool
    created_at: datetime


class AdminEducatorItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    display_name: str
    status: str
    created_at: datetime
    approved_at: Optional[datetime] = None
    approved_by_admin_id: Optional[str] = None


class EducatorApprovalResponse(BaseModel):
    id: str
    email: str
    status: str
    approved_at: datetime
    approved_by_admin_id: str


class EducatorSuspensionResponse(BaseModel):
    id: str
    email: str
    status: str
