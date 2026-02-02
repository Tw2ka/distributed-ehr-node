from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from uuid import UUID, uuid4


# Nested models for structured patient data
class IdentityInfo(BaseModel):
    """Patient identity information"""
    patientId: str = Field(..., description="Unique patient identifier")
    mrn: Optional[str] = Field(None, description="Medical Record Number")
    nationalId: Optional[str] = Field(None, description="National ID (hashed)")


class NameInfo(BaseModel):
    """Patient name structure"""
    given: str = Field(..., description="Given name")
    family: str = Field(..., description="Family name")


class Demographics(BaseModel):
    """Patient demographics"""
    name: NameInfo
    dob: date = Field(..., description="Date of birth")
    sexAtBirth: Optional[str] = Field(None, description="Sex at birth")
    genderIdentity: Optional[str] = Field(None, description="Gender identity")
    deceased: bool = Field(default=False)


class ContactInfo(BaseModel):
    """Patient contact information"""
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class Encounter(BaseModel):
    """Individual encounter/visit record"""
    encounterId: str
    type: str = Field(..., description="encounter type: outpatient, inpatient, emergency")
    start: datetime
    end: Optional[datetime] = None
    location: Optional[str] = None
    provider: Optional[str] = None
    reason: Optional[str] = None


class Condition(BaseModel):
    """Patient condition/diagnosis"""
    id: str
    code: Optional[str] = None
    system: Optional[str] = Field(None, description="e.g., ICD-10")
    description: str
    onset: Optional[date] = None
    status: str = Field(default="active", description="active, resolved, etc.")
    recordedAt: datetime
    encounterId: Optional[str] = None


class Allergy(BaseModel):
    """Patient allergy information"""
    substance: str
    reaction: Optional[str] = None
    severity: Optional[str] = Field(None, description="mild, moderate, severe")
    status: str = Field(default="active")
    recordedAt: datetime


class Medication(BaseModel):
    """Active medication"""
    medId: str
    drug: str
    dose: Optional[str] = None
    route: Optional[str] = None
    frequency: Optional[str] = None
    start: date
    end: Optional[date] = None
    prescriber: Optional[str] = None


class MedicationHistory(BaseModel):
    """Historical medication record"""
    drug: str
    start: date
    end: Optional[date] = None
    reasonStopped: Optional[str] = None


class MedicationsInfo(BaseModel):
    """Medications section"""
    active: List[Medication] = Field(default_factory=list)
    history: List[MedicationHistory] = Field(default_factory=list)


class ConsentInfo(BaseModel):
    """Patient consent information"""
    allowed: bool = Field(default=True)
    scope: List[str] = Field(default_factory=list)
    grantedAt: Optional[datetime] = None


class ConsentsInfo(BaseModel):
    """Consents section"""
    dataSharing: Optional[ConsentInfo] = None


class MetaInfo(BaseModel):
    """Metadata for distributed system"""
    sourceHospital: str = Field(..., description="Name of the source node/hospital")
    replicaVector: Dict[str, Any] = Field(default_factory=dict, description="For distributed consensus")


# Input models for API
class PatientCreate(BaseModel):
    """Model for creating a new patient"""
    identity: IdentityInfo
    demographics: Demographics
    contacts: Optional[ContactInfo] = None
    sourceHospital: str = Field(..., description="Name of the hospital node")


class PatientUpdate(BaseModel):
    """Model for updating patient - all fields optional"""
    demographics: Optional[Demographics] = None
    contacts: Optional[ContactInfo] = None
    encounters: Optional[List[Encounter]] = None
    conditions: Optional[List[Condition]] = None
    allergies: Optional[List[Allergy]] = None
    medications: Optional[MedicationsInfo] = None
    consents: Optional[ConsentsInfo] = None


# Main Patient Document for MongoDB
class Patient(Document):
    """
    Longitudinal patient record stored as a single MongoDB document.
    Designed for distributed EHR system with eventual consistency.
    """
    # Document metadata
    id: UUID = Field(default_factory=uuid4, description="Internal UUID")
    version: int = Field(default=1, description="Document version for optimistic locking")
    lastUpdated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Core patient information
    identity: IdentityInfo
    demographics: Demographics
    contacts: Optional[ContactInfo] = None

    # Clinical data (time-ordered arrays)
    conditions: List[Condition] = Field(default_factory=list)
    allergies: List[Allergy] = Field(default_factory=list)

    # Distributed system metadata
    meta: MetaInfo

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "patients"
        use_state_management = True
        indexes = [
            "identity.patientId",  # Index on patientId for fast lookups
            "identity.mrn",
            "created_at",
        ]

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
