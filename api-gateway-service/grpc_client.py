import grpc
from proto import ehr_service_pb2_grpc, ehr_service_pb2
from models import BloodType


# Mapping between API models and protobuf blood types
BLOOD_TYPE_TO_PROTO = {
    BloodType.A_POSITIVE: ehr_service_pb2.A_POSITIVE,
    BloodType.A_NEGATIVE: ehr_service_pb2.A_NEGATIVE,
    BloodType.B_POSITIVE: ehr_service_pb2.B_POSITIVE,
    BloodType.B_NEGATIVE: ehr_service_pb2.B_NEGATIVE,
    BloodType.AB_POSITIVE: ehr_service_pb2.AB_POSITIVE,
    BloodType.AB_NEGATIVE: ehr_service_pb2.AB_NEGATIVE,
    BloodType.O_POSITIVE: ehr_service_pb2.O_POSITIVE,
    BloodType.O_NEGATIVE: ehr_service_pb2.O_NEGATIVE,
}

BLOOD_TYPE_FROM_PROTO = {
    ehr_service_pb2.A_POSITIVE: BloodType.A_POSITIVE,
    ehr_service_pb2.A_NEGATIVE: BloodType.A_NEGATIVE,
    ehr_service_pb2.B_POSITIVE: BloodType.B_POSITIVE,
    ehr_service_pb2.B_NEGATIVE: BloodType.B_NEGATIVE,
    ehr_service_pb2.AB_POSITIVE: BloodType.AB_POSITIVE,
    ehr_service_pb2.AB_NEGATIVE: BloodType.AB_NEGATIVE,
    ehr_service_pb2.O_POSITIVE: BloodType.O_POSITIVE,
    ehr_service_pb2.O_NEGATIVE: BloodType.O_NEGATIVE,
}


class GrpcClient:
    """gRPC client for EHR service"""

    def __init__(self, host: str = 'localhost', port: int = 50051):
        """Initialize gRPC client with server address"""
        self.address = f'{host}:{port}'
        self.channel = None
        self.stub = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.channel = grpc.aio.insecure_channel(self.address)
        self.stub = ehr_service_pb2_grpc.EhrServiceStub(self.channel)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.channel:
            await self.channel.close()

    async def create_patient(self, patient_data: dict) -> dict:
        """Create a new patient via gRPC"""
        request = ehr_service_pb2.CreatePatientRequest(
            patient_id=patient_data['patient_id'],
            name=patient_data['name'],
            birth_date=patient_data['birth_date'].isoformat(),
            height=patient_data['height'],
            weight=patient_data['weight'],
            blood_type=BLOOD_TYPE_TO_PROTO[patient_data['blood_type']],
            diagnosis=patient_data['diagnosis']
        )

        response = await self.stub.CreatePatient(request)
        return self._patient_proto_to_dict(response.patient)

    async def get_patient(self, patient_uuid: str) -> dict:
        """Get a patient by UUID via gRPC"""
        request = ehr_service_pb2.GetPatientRequest(patient_uuid=patient_uuid)
        response = await self.stub.GetPatient(request)
        return self._patient_proto_to_dict(response.patient)

    async def get_all_patients(self, skip: int = 0, limit: int = 100) -> list:
        """Get all patients with pagination via gRPC"""
        request = ehr_service_pb2.GetAllPatientsRequest(skip=skip, limit=limit)
        response = await self.stub.GetAllPatients(request)
        return [self._patient_proto_to_dict(p) for p in response.patients]

    async def search_patient_by_id(self, patient_id: str) -> dict:
        """Search for a patient by patient_id via gRPC"""
        request = ehr_service_pb2.SearchPatientByIdRequest(patient_id=patient_id)
        response = await self.stub.SearchPatientById(request)
        return self._patient_proto_to_dict(response.patient)

    async def update_patient(self, patient_uuid: str, patient_data: dict) -> dict:
        """Update a patient via gRPC"""
        # Build request with only provided fields
        kwargs = {'patient_uuid': patient_uuid}

        if 'patient_id' in patient_data and patient_data['patient_id'] is not None:
            kwargs['patient_id'] = patient_data['patient_id']
        if 'name' in patient_data and patient_data['name'] is not None:
            kwargs['name'] = patient_data['name']
        if 'birth_date' in patient_data and patient_data['birth_date'] is not None:
            kwargs['birth_date'] = patient_data['birth_date'].isoformat()
        if 'height' in patient_data and patient_data['height'] is not None:
            kwargs['height'] = patient_data['height']
        if 'weight' in patient_data and patient_data['weight'] is not None:
            kwargs['weight'] = patient_data['weight']
        if 'blood_type' in patient_data and patient_data['blood_type'] is not None:
            kwargs['blood_type'] = BLOOD_TYPE_TO_PROTO[patient_data['blood_type']]
        if 'diagnosis' in patient_data and patient_data['diagnosis'] is not None:
            kwargs['diagnosis'] = patient_data['diagnosis']

        request = ehr_service_pb2.UpdatePatientRequest(**kwargs)
        response = await self.stub.UpdatePatient(request)
        return self._patient_proto_to_dict(response.patient)

    async def delete_patient(self, patient_uuid: str) -> dict:
        """Delete a patient via gRPC"""
        request = ehr_service_pb2.DeletePatientRequest(patient_uuid=patient_uuid)
        response = await self.stub.DeletePatient(request)
        return {
            'success': response.success,
            'message': response.message
        }

    def _patient_proto_to_dict(self, patient_proto) -> dict:
        """Convert protobuf patient message to dictionary"""
        return {
            'id': patient_proto.id,
            'patient_id': patient_proto.patient_id,
            'name': patient_proto.name,
            'birth_date': patient_proto.birth_date,
            'height': patient_proto.height,
            'weight': patient_proto.weight,
            'blood_type': BLOOD_TYPE_FROM_PROTO[patient_proto.blood_type],
            'diagnosis': patient_proto.diagnosis,
            'created_at': patient_proto.created_at,
            'updated_at': patient_proto.updated_at
        }
