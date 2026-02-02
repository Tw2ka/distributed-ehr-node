import asyncio
import grpc
from concurrent import futures
from uuid import UUID
from datetime import date, datetime
import os
from dotenv import load_dotenv
from google.protobuf.struct_pb2 import Struct, ListValue
from google.protobuf.json_format import MessageToDict

from proto import ehr_service_pb2_grpc, ehr_service_pb2

import crud_service
from database import Database
from models import PatientCreate, PatientUpdate

load_dotenv()  # This loads the .env file

# gRPC server configuration from environment variables
GRPC_HOST = os.getenv('GRPC_HOST', '0.0.0.0')
GRPC_PORT = int(os.getenv('GRPC_PORT', '50051'))


def parse_dates_recursive(obj):
    """Recursively parse ISO date strings to date objects"""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            # Parse specific date fields
            if key == 'dob' and isinstance(value, str):
                try:
                    result[key] = date.fromisoformat(value)
                except:
                    result[key] = value
            elif key in ['start', 'end', 'recordedAt', 'grantedAt'] and isinstance(value, str):
                try:
                    result[key] = datetime.fromisoformat(value)
                except:
                    result[key] = value
            else:
                result[key] = parse_dates_recursive(value)
        return result
    elif isinstance(obj, list):
        return [parse_dates_recursive(item) for item in obj]
    else:
        return obj


def dict_to_struct(data: dict) -> Struct:
    """Convert Python dict to protobuf Struct"""
    struct = Struct()
    struct.update(data)
    return struct


def list_to_listvalue(data: list) -> ListValue:
    """Convert Python list to protobuf ListValue"""
    list_value = ListValue()
    for item in data:
        if isinstance(item, dict):
            # Convert dict items to Struct
            struct = Struct()
            struct.update(item)
            list_value.values.add().struct_value.CopyFrom(struct)
        else:
            # Handle primitive types
            list_value.values.add().string_value = str(item)
    return list_value


def patient_to_proto(patient) -> ehr_service_pb2.PatientMessage:
    """Convert a Patient model to protobuf PatientMessage"""
    # Convert patient to dict
    patient_dict = patient.model_dump(mode='json')

    # Convert conditions and allergies lists to ListValue
    conditions_list = patient_dict.get('conditions', [])
    allergies_list = patient_dict.get('allergies', [])

    return ehr_service_pb2.PatientMessage(
        id=str(patient.id),
        version=patient.version,
        lastUpdated=patient.lastUpdated.isoformat(),
        identity=dict_to_struct(patient_dict.get('identity', {})),
        demographics=dict_to_struct(patient_dict.get('demographics', {})),
        contacts=dict_to_struct(patient_dict.get('contacts', {})) if patient_dict.get('contacts') else Struct(),
        conditions=list_to_listvalue(conditions_list),
        allergies=list_to_listvalue(allergies_list),
        meta=dict_to_struct(patient_dict.get('meta', {})),
        created_at=patient.created_at.isoformat(),
        updated_at=patient.updated_at.isoformat(),
    )




class EhrServiceServicer(ehr_service_pb2_grpc.EhrServiceServicer):
    """gRPC servicer implementation for EHR Service"""

    async def CreatePatient(self, request, context):
        """Create a new patient record"""
        try:
            # Convert protobuf Struct to dict
            patient_data = MessageToDict(request.patientData)

            # Parse date strings to date/datetime objects
            patient_data = parse_dates_recursive(patient_data)

            # Create PatientCreate object
            patient_create = PatientCreate(**patient_data)

            # Create patient in database
            new_patient = await crud_service.create_patient(patient_create)

            # Convert to proto and return
            return ehr_service_pb2.PatientResponse(
                patient=patient_to_proto(new_patient)
            )

        except ValueError as e:
            # Handle duplicate patientId error
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(str(e))
            return ehr_service_pb2.PatientResponse()
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

            # Convert protobuf Struct to dict
            update_data = MessageToDict(request.updateData)

            # Parse date strings to date/datetime objects
            update_data = parse_dates_recursive(update_data)

            # Create PatientUpdate object
            patient_update = PatientUpdate(**update_data)

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
                context.set_details(f"Patient with UUID {patient_uuid} not found")
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

    # Bind to port using environment variables
    listen_addr = f'{GRPC_HOST}:{GRPC_PORT}'
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
