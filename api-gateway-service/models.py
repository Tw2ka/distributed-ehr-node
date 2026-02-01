from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum


class BloodType(str, Enum):
    """Blood type enumeration matching the gRPC proto definition"""
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class PatientBase(BaseModel):
    """Base patient model with common fields"""
    patient_id: str = Field(..., description="Patient identifier", example="P001")
    name: str = Field(..., min_length=1, max_length=255, example="John Doe")
    birth_date: date = Field(..., example="1990-01-15")
    height: int = Field(..., gt=0, description="Height in cm", example=175)
    weight: int = Field(..., gt=0, description="Weight in kg", example=70)
    blood_type: BloodType = Field(..., example="A+")
    diagnosis: str = Field(..., max_length=255, example="Healthy")


class PatientCreate(PatientBase):
    """Model for creating a new patient"""
    pass


class PatientUpdate(BaseModel):
    """Model for updating a patient (all fields optional)"""
    patient_id: Optional[str] = Field(None, description="Patient identifier", example="P001")
    name: Optional[str] = Field(None, min_length=1, max_length=255, example="John Doe")
    birth_date: Optional[date] = Field(None, example="1990-01-15")
    height: Optional[int] = Field(None, gt=0, description="Height in cm", example=175)
    weight: Optional[int] = Field(None, gt=0, description="Weight in kg", example=70)
    blood_type: Optional[BloodType] = Field(None, example="A+")
    diagnosis: Optional[str] = Field(None, max_length=255, example="Healthy")


class PatientResponse(PatientBase):
    """Model for patient response including generated fields"""
    id: str = Field(..., description="UUID of the patient", example="550e8400-e29b-41d4-a716-446655440000")
    created_at: datetime = Field(..., example="2026-01-26T10:00:00Z")
    updated_at: datetime = Field(..., example="2026-01-26T10:00:00Z")

    class Config:
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
                "created_at": "2026-01-26T10:00:00Z",
                "updated_at": "2026-01-26T10:00:00Z"
            }
        }


class DeleteResponse(BaseModel):
    """Response model for delete operations"""
    success: bool
    message: str


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
