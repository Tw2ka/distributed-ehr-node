import asyncio
import grpc

from proto import ehr_service_pb2_grpc, ehr_service_pb2


async def run_client_demo():
    """Demo gRPC client showing all operations"""

    # Create a gRPC channel
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        # Create a stub (client)
        stub = ehr_service_pb2_grpc.EHRServiceStub(channel)

        print("=" * 60)
        print("EHR CRUD Service - gRPC Client Demo")
        print("=" * 60)

        # 1. Create a patient
        print("\n1. Creating a new patient...")
        create_request = ehr_service_pb2.CreatePatientRequest(
            patient_id="P001",
            name="John Doe",
            birth_date="1990-01-15",
            height=175,
            weight=70,
            blood_type=ehr_service_pb2.A_POSITIVE,
            diagnosis="Healthy"
        )

        try:
            create_response = await stub.CreatePatient(create_request)
            patient_uuid = create_response.patient.id
            print(f"✓ Patient created successfully!")
            print(f"  UUID: {patient_uuid}")
            print(f"  Patient ID: {create_response.patient.patient_id}")
            print(f"  Name: {create_response.patient.name}")
            print(f"  Birth Date: {create_response.patient.birth_date}")
            print(f"  Blood Type: {ehr_service_pb2.BloodType.Name(create_response.patient.blood_type)}")
        except grpc.aio.AioRpcError as e:
            print(f"✗ Error: {e.details()}")
            return

        # 2. Get patient by UUID
        print(f"\n2. Retrieving patient by UUID...")
        get_request = ehr_service_pb2.GetPatientRequest(
            patient_uuid=patient_uuid
        )

        try:
            get_response = await stub.GetPatient(get_request)
            print(f"✓ Patient retrieved successfully!")
            print(f"  Name: {get_response.patient.name}")
            print(f"  Height: {get_response.patient.height} cm")
            print(f"  Weight: {get_response.patient.weight} kg")
        except grpc.aio.AioRpcError as e:
            print(f"✗ Error: {e.details()}")

        # 3. Search patient by patient_id
        print(f"\n3. Searching patient by patient_id...")
        search_request = ehr_service_pb2.SearchPatientByIdRequest(
            patient_id="P001"
        )

        try:
            search_response = await stub.SearchPatientById(search_request)
            print(f"✓ Patient found!")
            print(f"  Name: {search_response.patient.name}")
            print(f"  Diagnosis: {search_response.patient.diagnosis}")
        except grpc.aio.AioRpcError as e:
            print(f"✗ Error: {e.details()}")

        # 4. Update patient
        print(f"\n4. Updating patient diagnosis...")
        update_request = ehr_service_pb2.UpdatePatientRequest(
            patient_uuid=patient_uuid,
            diagnosis="Routine checkup - All normal",
            weight=72  # Weight increased by 2kg
        )

        try:
            update_response = await stub.UpdatePatient(update_request)
            print(f"✓ Patient updated successfully!")
            print(f"  New Diagnosis: {update_response.patient.diagnosis}")
            print(f"  New Weight: {update_response.patient.weight} kg")
        except grpc.aio.AioRpcError as e:
            print(f"✗ Error: {e.details()}")

        # 5. Get all patients
        print(f"\n5. Retrieving all patients...")
        list_request = ehr_service_pb2.GetAllPatientsRequest(
            skip=0,
            limit=10
        )

        try:
            list_response = await stub.GetAllPatients(list_request)
            print(f"✓ Retrieved {len(list_response.patients)} patient(s):")
            for idx, patient in enumerate(list_response.patients, 1):
                print(f"  {idx}. {patient.name} (ID: {patient.patient_id})")
        except grpc.aio.AioRpcError as e:
            print(f"✗ Error: {e.details()}")

        # 6. Delete patient
        print(f"\n6. Deleting patient...")
        delete_request = ehr_service_pb2.DeletePatientRequest(
            patient_uuid=patient_uuid
        )

        try:
            delete_response = await stub.DeletePatient(delete_request)
            if delete_response.success:
                print(f"✓ {delete_response.message}")
            else:
                print(f"✗ {delete_response.message}")
        except grpc.aio.AioRpcError as e:
            print(f"✗ Error: {e.details()}")

        print("\n" + "=" * 60)
        print("Demo completed!")
        print("=" * 60)


async def create_patient_example():
    """Simple example: Create a patient"""
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = ehr_service_pb2_grpc.EHRServiceStub(channel)

        request = ehr_service_pb2.CreatePatientRequest(
            patient_id="P002",
            name="Jane Smith",
            birth_date="1985-05-20",
            height=165,
            weight=60,
            blood_type=ehr_service_pb2.O_POSITIVE,
            diagnosis="Hypertension"
        )

        response = await stub.CreatePatient(request)
        print(f"Created patient: {response.patient.name} (UUID: {response.patient.id})")


async def get_all_patients_example():
    """Simple example: Get all patients"""
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = ehr_service_pb2_grpc.EHRServiceStub(channel)

        request = ehr_service_pb2.GetAllPatientsRequest(skip=0, limit=100)
        response = await stub.GetAllPatients(request)

        print(f"Total patients: {len(response.patients)}")
        for patient in response.patients:
            print(f"  - {patient.name} (ID: {patient.patient_id})")


if __name__ == '__main__':
    # Run the full demo
    asyncio.run(run_client_demo())

    # Or run individual examples:
    # asyncio.run(create_patient_example())
    # asyncio.run(get_all_patients_example())
