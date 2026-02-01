import asyncio
import grpc
from concurrent import futures
from uuid import UUID
from datetime import date

from proto import ehr_service_pb2_grpc, ehr_service_pb2

import crud_service
from database import Database
from models import PatientCreate, PatientUpdate, BloodType as ModelBloodType


# Mapping between protobuf and model blood types
BLOOD_TYPE_PROTO_TO_MODEL = {
    ehr_service_pb2.A_POSITIVE: ModelBloodType.A_POSITIVE,
    ehr_service_pb2.A_NEGATIVE: ModelBloodType.A_NEGATIVE,
    ehr_service_pb2.B_POSITIVE: ModelBloodType.B_POSITIVE,
    ehr_service_pb2.B_NEGATIVE: ModelBloodType.B_NEGATIVE,
    ehr_service_pb2.AB_POSITIVE: ModelBloodType.AB_POSITIVE,
    ehr_service_pb2.AB_NEGATIVE: ModelBloodType.AB_NEGATIVE,
    ehr_service_pb2.O_POSITIVE: ModelBloodType.O_POSITIVE,
    ehr_service_pb2.O_NEGATIVE: ModelBloodType.O_NEGATIVE,
}

BLOOD_TYPE_MODEL_TO_PROTO = {
    ModelBloodType.A_POSITIVE: ehr_service_pb2.A_POSITIVE,
    ModelBloodType.A_NEGATIVE: ehr_service_pb2.A_NEGATIVE,
    ModelBloodType.B_POSITIVE: ehr_service_pb2.B_POSITIVE,
    ModelBloodType.B_NEGATIVE: ehr_service_pb2.B_NEGATIVE,
    ModelBloodType.AB_POSITIVE: ehr_service_pb2.AB_POSITIVE,
    ModelBloodType.AB_NEGATIVE: ehr_service_pb2.AB_NEGATIVE,
    ModelBloodType.O_POSITIVE: ehr_service_pb2.O_POSITIVE,
    ModelBloodType.O_NEGATIVE: ehr_service_pb2.O_NEGATIVE,
}


def patient_to_proto(patient) -> ehr_service_pb2.PatientMessage:
    """Convert a Patient model to protobuf PatientMessage"""
    return ehr_service_pb2.PatientMessage(
        id=str(patient.id),
        patient_id=patient.patient_id,
        name=patient.name,
        birth_date=patient.birth_date.isoformat(),
        height=patient.height,
        weight=patient.weight,
        blood_type=BLOOD_TYPE_MODEL_TO_PROTO[patient.blood_type],
        diagnosis=patient.diagnosis,
        created_at=patient.created_at.isoformat(),
        updated_at=patient.updated_at.isoformat(),
    )


class EhrServiceServicer(ehr_service_pb2_grpc.EhrServiceServicer):
    """gRPC servicer implementation for EHR Service"""

    async def CreatePatient(self, request, context):
        """Create a new patient record"""
        try:
            # Convert proto blood type to model blood type
            blood_type = BLOOD_TYPE_PROTO_TO_MODEL.get(request.blood_type)
            if blood_type is None:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Invalid blood type')
                return ehr_service_pb2.PatientResponse()

            # Parse birth date
            birth_date = date.fromisoformat(request.birth_date)

            # Create PatientCreate object
            patient_create = PatientCreate(
                patient_id=request.patient_id,
                name=request.name,
                birth_date=birth_date,
                height=request.height,
                weight=request.weight,
                blood_type=blood_type,
                diagnosis=request.diagnosis
            )

            # Create patient in database
            new_patient = await crud_service.create_patient(patient_create)

            # Convert to proto and return
            return ehr_service_pb2.PatientResponse(
                patient=patient_to_proto(new_patient)
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Error creating patient: {str(e)}')
            return ehr_service_pb2.PatientResponse()

    async def GetPatient(self, request, context):
        """Get a patient by UUID"""
        try:
            # Parse UUID
            try:
                patient_uuid = UUID(request.patient_uuid)
            except ValueError:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Invalid UUID format')
                return ehr_service_pb2.PatientResponse()

            # Get patient from database
            patient = await crud_service.get_patient(patient_uuid)

            if patient is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f'Patient with UUID {patient_uuid} not found')
                return ehr_service_pb2.PatientResponse()

            # Convert to proto and return
            return ehr_service_pb2.PatientResponse(
                patient=patient_to_proto(patient)
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Error retrieving patient: {str(e)}')
            return ehr_service_pb2.PatientResponse()

    async def GetAllPatients(self, request, context):
        """Get all patients with pagination"""
        try:
            skip = request.skip if request.skip > 0 else 0
            limit = request.limit if request.limit > 0 else 100

            # Get patients from database
            patients = await crud_service.get_all_patients(skip=skip, limit=limit)

            # Convert to proto
            patient_messages = [patient_to_proto(p) for p in patients]

            return ehr_service_pb2.GetAllPatientsResponse(
                patients=patient_messages
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Error retrieving patients: {str(e)}')
            return ehr_service_pb2.GetAllPatientsResponse()

    async def SearchPatientById(self, request, context):
        """Search for a patient by patient_id"""
        try:
            # Get patient from database
            patient = await crud_service.get_patient_by_patient_id(request.patient_id)

            if patient is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f'Patient with patient_id {request.patient_id} not found')
                return ehr_service_pb2.PatientResponse()

            # Convert to proto and return
            return ehr_service_pb2.PatientResponse(
                patient=patient_to_proto(patient)
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Error searching patient: {str(e)}')
            return ehr_service_pb2.PatientResponse()

    async def UpdatePatient(self, request, context):
        """Update a patient record"""
        try:
            # Parse UUID
            try:
                patient_uuid = UUID(request.patient_uuid)
            except ValueError:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Invalid UUID format')
                return ehr_service_pb2.PatientResponse()

            # Build update dict with only provided fields
            update_dict = {}

            if request.HasField('patient_id'):
                update_dict['patient_id'] = request.patient_id
            if request.HasField('name'):
                update_dict['name'] = request.name
            if request.HasField('birth_date'):
                update_dict['birth_date'] = date.fromisoformat(request.birth_date)
            if request.HasField('height'):
                update_dict['height'] = request.height
            if request.HasField('weight'):
                update_dict['weight'] = request.weight
            if request.HasField('blood_type'):
                blood_type = BLOOD_TYPE_PROTO_TO_MODEL.get(request.blood_type)
                if blood_type:
                    update_dict['blood_type'] = blood_type
            if request.HasField('diagnosis'):
                update_dict['diagnosis'] = request.diagnosis

            # Create PatientUpdate object
            patient_update = PatientUpdate(**update_dict)

            # Update patient in database
            updated_patient = await crud_service.update_patient(patient_uuid, patient_update)

            if updated_patient is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f'Patient with UUID {patient_uuid} not found')
                return ehr_service_pb2.PatientResponse()

            # Convert to proto and return
            return ehr_service_pb2.PatientResponse(
                patient=patient_to_proto(updated_patient)
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Error updating patient: {str(e)}')
            return ehr_service_pb2.PatientResponse()

    async def DeletePatient(self, request, context):
        """Delete a patient record"""
        try:
            # Parse UUID
            try:
                patient_uuid = UUID(request.patient_uuid)
            except ValueError:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Invalid UUID format')
                return ehr_service_pb2.DeletePatientResponse(success=False, message='Invalid UUID format')

            # Delete patient from database
            deleted = await crud_service.delete_patient(patient_uuid)

            if not deleted:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return ehr_service_pb2.DeletePatientResponse(
                    success=False,
                    message=f'Patient with UUID {patient_uuid} not found'
                )

            return ehr_service_pb2.DeletePatientResponse(
                success=True,
                message='Patient deleted successfully'
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Error deleting patient: {str(e)}')
            return ehr_service_pb2.DeletePatientResponse(
                success=False,
                message=f'Error deleting patient: {str(e)}'
            )


async def serve():
    """Start the gRPC server"""
    # Initialize database
    await Database.initialize()
    print("Database initialized successfully")

    # Create gRPC server
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add servicer to server
    ehr_service_pb2_grpc.add_EhrServiceServicer_to_server(
        EhrServiceServicer(), server
    )

    # Bind to port
    listen_addr = 'localhost:50051'
    server.add_insecure_port(listen_addr)

    print(f"Starting gRPC server on {listen_addr}")
    await server.start()
    print("gRPC server started successfully")

    try:
        await server.wait_for_termination()
    finally:
        await Database.close_connection()
        print("Database connection closed")


if __name__ == '__main__':
    print("EHR CRUD Service - gRPC Server")
    print("=" * 50)
    asyncio.run(serve())
