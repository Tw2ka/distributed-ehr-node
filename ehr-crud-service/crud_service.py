from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from models import Patient, PatientCreate, PatientUpdate

# SQLAlchemy-style CRUD operations using Beanie ORM for MongoDB
# Beanie provides an ORM interface similar to SQLAlchemy

async def create_patient(patient: PatientCreate) -> Patient:
    """
    Create a new patient record using ORM
    Similar to SQLAlchemy:
        patient = Patient(**data)
        session.add(patient)
        session.commit()
    """
    # Create Patient document instance from input data
    patient_obj = Patient(**patient.model_dump())

    # Save to database (ORM .insert() method)
    await patient_obj.insert()

    return patient_obj


async def get_patient(patient_uuid: UUID) -> Optional[Patient]:
    """
    Retrieve a patient by UUID using ORM
    Similar to SQLAlchemy:
        session.query(Patient).filter(Patient.id == uuid).first()
    or:
        session.get(Patient, uuid)
    """
    return await Patient.find_one(Patient.id == patient_uuid)


async def get_all_patients(skip: int = 0, limit: int = 100) -> List[Patient]:
    """
    Retrieve all patients with pagination using ORM
    Similar to SQLAlchemy:
        session.query(Patient).offset(skip).limit(limit).all()
    """
    return await Patient.find_all().skip(skip).limit(limit).to_list()


async def update_patient(patient_uuid: UUID, patient_update: PatientUpdate) -> Optional[Patient]:
    """
    Update a patient record using ORM
    Similar to SQLAlchemy:
        patient = session.get(Patient, uuid)
        patient.name = new_name
        session.commit()
    """
    # Find the patient (like SQLAlchemy query)
    patient = await Patient.find_one(Patient.id == patient_uuid)

    if not patient:
        return None

    # Get only the fields that were actually set
    update_data = patient_update.model_dump(exclude_unset=True)

    if not update_data:
        return patient

    # Update the updated_at timestamp
    update_data["updated_at"] = datetime.now(timezone.utc)

    # Update the document (ORM .set() method - similar to SQLAlchemy attribute assignment)
    await patient.set(update_data)

    return patient


async def delete_patient(patient_uuid: UUID) -> bool:
    """
    Delete a patient record using ORM
    Similar to SQLAlchemy:
        patient = session.get(Patient, uuid)
        session.delete(patient)
        session.commit()
    """
    patient = await Patient.find_one(Patient.id == patient_uuid)

    if not patient:
        return False

    # Delete the document (ORM .delete() method)
    await patient.delete()
    return True


async def get_patient_by_patient_id(patient_id: str) -> Optional[Patient]:
    """
    Retrieve a patient by patient_id field using ORM
    Similar to SQLAlchemy:
        session.query(Patient).filter(Patient.patient_id == patient_id).first()
    or:
        session.query(Patient).filter_by(patient_id=patient_id).first()
    """
    return await Patient.find_one(Patient.patient_id == patient_id)
