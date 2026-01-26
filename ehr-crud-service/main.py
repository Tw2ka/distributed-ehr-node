from contextlib import asynccontextmanager
from typing import List
from uuid import UUID

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

import crud_service
from database import Database
from models import Patient, PatientCreate, PatientUpdate


# async def insert_initial_data():
#     """Insert initial patient data on startup if it doesn't exist"""
#     try:
#         # Check if patient P001 already exists
#         existing_patient = await crud_service.get_patient_by_patient_id("P001")
#
#         if existing_patient is None:
#             # Create initial patient data
#             initial_patient = PatientCreate(
#                 patient_id="P001",
#                 name="John Doe",
#                 birth_date=date(1990, 1, 15),
#                 height=175,
#                 weight=70,
#                 blood_type=BloodType.A_POSITIVE,
#                 diagnosis="Healthy"
#             )
#
#             # Insert the patient
#             await crud_service.create_patient(initial_patient)
#             print("Initial patient data inserted: P001 - John Doe")
#         else:
#             print("Initial patient data already exists: P001 - John Doe")
#     except Exception as e:
#         print(f"Error inserting initial data: {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown events"""
    # Startup: Initialize database and Beanie ORM
    await Database.initialize()

    # Insert initial data if needed
    # await insert_initial_data()

    yield
    # Shutdown: Close database connection
    await Database.close_connection()


app = FastAPI(
    title="EHR Patient Management API",
    description="CRUD API for Electronic Health Records - Patient Data",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {
        "message": "EHR Patient Management API",
        "version": "1.0.0",
        "endpoints": {
            "create": "POST /patients/",
            "read_all": "GET /patients/",
            "read_one": "GET /patients/{patient_uuid}",
            "update": "PUT /patients/{patient_uuid}",
            "delete": "DELETE /patients/{patient_uuid}",
            "search": "GET /patients/search/{patient_id}"
        }
    }


@app.post(
    "/patients/",
    response_model=Patient,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new patient record",
    tags=["Patients"]
)
async def create_patient(patient: PatientCreate):
    """
    Create a new patient record with the following information:
    - **patient_id**: Unique patient identifier
    - **name**: Patient's full name
    - **birth_date**: Date of birth (YYYY-MM-DD)
    - **height**: Height in centimeters
    - **weight**: Weight in kilograms
    - **blood_type**: Blood type (A+, A-, B+, B-, AB+, AB-, O+, O-)
    - **diagnosis**: Medical diagnosis
    """
    try:
        new_patient = await crud_service.create_patient(patient)
        return new_patient
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating patient: {str(e)}"
        )


@app.get(
    "/patients/",
    response_model=List[Patient],
    summary="Get all patients",
    tags=["Patients"]
)
async def get_patients(skip: int = 0, limit: int = 100):
    """
    Retrieve all patient records with pagination:
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    """
    try:
        patients = await crud_service.get_all_patients(skip=skip, limit=limit)
        return patients
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving patients: {str(e)}"
        )


@app.get(
    "/patients/{patient_uuid}",
    response_model=Patient,
    summary="Get a patient by UUID",
    tags=["Patients"]
)
async def get_patient(patient_uuid: UUID):
    """
    Retrieve a specific patient record by UUID
    """
    try:
        patient = await crud_service.get_patient(patient_uuid)
        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with UUID {patient_uuid} not found"
            )
        return patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving patient: {str(e)}"
        )


@app.get(
    "/patients/search/{patient_id}",
    response_model=Patient,
    summary="Search patient by patient ID",
    tags=["Patients"]
)
async def search_patient_by_id(patient_id: str):
    """
    Search for a patient by their patient_id field
    """
    try:
        patient = await crud_service.get_patient_by_patient_id(patient_id)
        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with patient_id '{patient_id}' not found"
            )
        return patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching patient: {str(e)}"
        )


@app.put(
    "/patients/{patient_uuid}",
    response_model=Patient,
    summary="Update a patient record",
    tags=["Patients"]
)
async def update_patient(patient_uuid: UUID, patient_update: PatientUpdate):
    """
    Update an existing patient record. Only provided fields will be updated.
    """
    try:
        updated_patient = await crud_service.update_patient(patient_uuid, patient_update)
        if updated_patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with UUID {patient_uuid} not found"
            )
        return updated_patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating patient: {str(e)}"
        )


@app.delete(
    "/patients/{patient_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a patient record",
    tags=["Patients"]
)
async def delete_patient(patient_uuid: UUID):
    """
    Delete a patient record by UUID
    """
    try:
        deleted = await crud_service.delete_patient(patient_uuid)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with UUID {patient_uuid} not found"
            )
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting patient: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
