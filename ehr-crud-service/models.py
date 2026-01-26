from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime, timezone
from uuid import UUID, uuid4
from enum import Enum

class BloodType(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

class PatientBase(BaseModel):
    patient_id: str = Field(..., description="Patient identifier")
    name: str = Field(..., min_length=1, max_length=255)
    birth_date: date
    height: int = Field(..., gt=0, description="Height in cm")
    weight: int = Field(..., gt=0, description="Weight in kg")
    blood_type: BloodType
    diagnosis: str = Field(..., max_length=255)

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    patient_id: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    birth_date: Optional[date] = None
    height: Optional[int] = Field(None, gt=0)
    weight: Optional[int] = Field(None, gt=0)
    blood_type: Optional[BloodType] = None
    diagnosis: Optional[str] = Field(None, max_length=255)

class Patient(Document):
    # Patient fields
    patient_id: str = Field(..., description="Patient identifier")
    name: str = Field(..., min_length=1, max_length=255)
    birth_date: date
    height: int = Field(..., gt=0, description="Height in cm")
    weight: int = Field(..., gt=0, description="Weight in kg")
    blood_type: BloodType
    diagnosis: str = Field(..., max_length=255)

    # Auto-generated fields
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "patients"  # Collection name in MongoDB
        use_state_management = True

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "patient_id": "P001",
                "name": "John Doe",
                "birth_date": "1990-01-15",
                "height": 175,
                "weight": 70,
                "blood_type": "A+",
                "diagnosis": "Healthy",
                "created_at": "2026-01-26T10:00:00",
                "updated_at": "2026-01-26T10:00:00"
            }
        }
