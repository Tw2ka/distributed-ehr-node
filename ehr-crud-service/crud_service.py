from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from models import Patient, PatientCreate, PatientUpdate, MetaInfo


async def create_patient(patient: PatientCreate) -> Patient:
    """
    Create a new patient record using ORM
    Checks for duplicate patientId before creating
    """
    # Check if patient with this patientId already exists
    existing_patient = await Patient.find_one(
        Patient.identity.patientId == patient.identity.patientId
    )

    if existing_patient:
        raise ValueError(f"Patient with patientId '{patient.identity.patientId}' already exists")

    # Create metadata
    meta = MetaInfo(
        sourceHospital=patient.sourceHospital,
        replicaVector={}
    )

    # Create Patient document instance from input data
    patient_dict = patient.model_dump(exclude={"sourceHospital"})
    patient_dict["meta"] = meta

    patient_obj = Patient(**patient_dict)

    # Save to database (ORM .insert() method)
    await patient_obj.insert()

    return patient_obj


async def get_patient(patient_uuid: UUID) -> Optional[Patient]:
    """
    Retrieve a patient by UUID using ORM
    """
    return await Patient.find_one(Patient.id == patient_uuid)


async def get_all_patients(skip: int = 0, limit: int = 100) -> List[Patient]:
    """
    Retrieve all patients with pagination using ORM
    """
    return await Patient.find_all().skip(skip).limit(limit).to_list()


async def update_patient(patient_uuid: UUID, patient_update: PatientUpdate) -> Optional[Patient]:
    """
    Update a patient record using ORM
    """
    # Find the patient
    patient = await Patient.find_one(Patient.id == patient_uuid)

    if not patient:
        return None

    # Get only the fields that were actually set
    update_data = patient_update.model_dump(exclude_unset=True)

    if not update_data:
        return patient

    # Update the updated_at timestamp and increment version
    update_data["updated_at"] = datetime.now(timezone.utc)
    update_data["lastUpdated"] = datetime.now(timezone.utc)
    update_data["version"] = patient.version + 1

    # Update the document
    await patient.set(update_data)

    return patient


async def delete_patient(patient_uuid: UUID) -> Optional[bool]:
    """
    Delete a patient record using ORM
    """
    patient = await Patient.find_one(Patient.id == patient_uuid)

    if not patient:
        return None

    await patient.delete()
    return True


async def get_patient_by_patient_id(patient_id: str) -> Optional[Patient]:
    """
    Retrieve a patient by patientId field using ORM
    """
    return await Patient.find_one(Patient.identity.patientId == patient_id)
