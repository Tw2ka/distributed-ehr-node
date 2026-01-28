# EHR API Gateway Service

A FastAPI-based REST API Gateway for the Distributed EHR (Electronic Health Records) System. This service acts as a bridge between REST API clients and the gRPC backend service.

## Overview

The API Gateway provides RESTful endpoints that internally communicate with the gRPC-based EHR CRUD service. This architecture separates the client-facing API from the backend microservice.

```
Client (REST) → API Gateway (FastAPI) → gRPC Server (EHR CRUD Service) → MongoDB
```

## Architecture Components

### 1. **main.py** - FastAPI Application
The main application file containing all REST API endpoints:
- `POST /patients` - Create a new patient
- `GET /patients/{patient_uuid}` - Get patient by UUID
- `GET /patients` - Get all patients (with pagination)
- `GET /patients/search/{patient_id}` - Search patient by patient_id
- `PUT /patients/{patient_uuid}` - Update patient (full update)
- `PATCH /patients/{patient_uuid}` - Update patient (partial update)
- `DELETE /patients/{patient_uuid}` - Delete patient

### 2. **models.py** - Pydantic Models
Defines the data models for request/response validation:
- `BloodType` - Enum for blood types
- `PatientBase` - Base patient fields
- `PatientCreate` - Model for creating patients
- `PatientUpdate` - Model for updating patients (all fields optional)
- `PatientResponse` - Model for patient responses (includes UUID and timestamps)
- `DeleteResponse` - Model for delete operation responses
- `ErrorResponse` - Model for error responses

### 3. **grpc_client.py** - gRPC Client Wrapper
A Python wrapper around the gRPC client that:
- Manages gRPC channel connections
- Translates between REST models and gRPC messages
- Handles blood type enum conversions
- Provides async context manager for connection management

### 4. **proto/** - Protocol Buffer Files

#### What are Protocol Buffers (Protobuf)?
Protocol Buffers are Google's language-neutral, platform-neutral mechanism for serializing structured data. They're like JSON or XML but:
- More compact (binary format)
- Faster to serialize/deserialize
- Strongly typed
- Language-agnostic

#### The Proto Files:

**ehr_service.proto** - The source definition file
- Written in Protocol Buffer Language
- Defines the gRPC service interface
- Defines message structures (like classes/schemas)
- Defines the RPC methods (like API endpoints)

**ehr_service_pb2.py** - Generated Message Classes
- Auto-generated from `.proto` file using `protoc` compiler
- Contains Python classes for all message types (PatientMessage, CreatePatientRequest, etc.)
- Contains enum definitions (BloodType)
- Handles serialization/deserialization of messages
- **DO NOT EDIT MANUALLY** - regenerate when .proto changes

**ehr_service_pb2_grpc.py** - Generated Service Classes
- Auto-generated from `.proto` file
- Contains gRPC stub classes (clients) and servicer classes (servers)
- `EhrServiceStub` - Client-side class for making RPC calls
- `EhrServiceServicer` - Server-side base class for implementing the service
- `add_EhrServiceServicer_to_server()` - Helper function to register the service
- **DO NOT EDIT MANUALLY** - regenerate when .proto changes

**ehr_service_pb2.pyi** - Type Hints File
- Provides type hints for the generated Python code
- Helps IDEs with autocomplete and type checking
- Makes the generated code easier to work with in Python

#### How pb2 and pb2_grpc Work Together:

1. **pb2 (Messages)**: Contains the data structures
   ```python
   # Create a request message
   request = ehr_service_pb2.CreatePatientRequest(
       patient_id="P001",
       name="John Doe",
       blood_type=ehr_service_pb2.A_POSITIVE
   )
   ```

2. **pb2_grpc (Service)**: Contains the RPC methods
   ```python
   # Create a client stub
   stub = ehr_service_pb2_grpc.EhrServiceStub(channel)
   
   # Call an RPC method with a message
   response = await stub.CreatePatient(request)
   ```

3. **Together**: pb2 provides the data, pb2_grpc provides the communication
   ```python
   # Full workflow
   channel = grpc.aio.insecure_channel('localhost:50051')
   stub = ehr_service_pb2_grpc.EhrServiceStub(channel)  # From pb2_grpc
   request = ehr_service_pb2.CreatePatientRequest(...)   # From pb2
   response = await stub.CreatePatient(request)          # pb2_grpc method + pb2 message
   ```

#### Do You Need Both?
**YES!** You need both files:
- **pb2.py** - For creating and working with messages (data)
- **pb2_grpc.py** - For making RPC calls (communication)

Think of it like:
- **pb2** = JSON schema + data structures
- **pb2_grpc** = HTTP client/server + routes

#### How They're Created:

```bash
# Install the gRPC tools
pip install grpcio-tools

# Generate both files from the .proto file
python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    --pyi_out=. \
    ehr_service.proto
```

This single command generates all three files:
- `ehr_service_pb2.py` (--python_out)
- `ehr_service_pb2_grpc.py` (--grpc_python_out)
- `ehr_service_pb2.pyi` (--pyi_out)

## Installation

```bash
# Navigate to the api-gateway-service directory
cd api-gateway-service

# Install dependencies
pip install -r requirements.txt
```

## Running the Service

### Prerequisites
1. MongoDB must be running
2. EHR CRUD Service (gRPC server) must be running on `localhost:50051`

### Start the API Gateway

```bash
# From the api-gateway-service directory
uvicorn main:app --reload --port 8000
```

The API will be available at:
- **API Endpoints**: http://localhost:8000
- **Interactive Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

## Example Usage

### Create a Patient

```bash
curl -X POST "http://localhost:8000/patients" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "name": "John Doe",
    "birth_date": "1990-01-15",
    "height": 175,
    "weight": 70,
    "blood_type": "A+",
    "diagnosis": "Healthy"
  }'
```

### Get All Patients

```bash
curl "http://localhost:8000/patients?skip=0&limit=10"
```

### Get Patient by UUID

```bash
curl "http://localhost:8000/patients/{uuid}"
```

### Update Patient

```bash
curl -X PUT "http://localhost:8000/patients/{uuid}" \
  -H "Content-Type: application/json" \
  -d '{
    "diagnosis": "Updated diagnosis",
    "weight": 72
  }'
```

### Delete Patient

```bash
curl -X DELETE "http://localhost:8000/patients/{uuid}"
```

## API Response Format

### Success Response (Patient)
```json
{
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
```

### Error Response
```json
{
  "detail": "Error message here"
}
```

## Development

### Project Structure

```
api-gateway-service/
├── main.py                 # FastAPI application with REST endpoints
├── models.py              # Pydantic models for request/response validation
├── grpc_client.py         # gRPC client wrapper
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── test_main.http        # HTTP test requests
└── proto/                # Protocol Buffer files
    ├── __init__.py
    ├── ehr_service.proto      # Proto definition (source)
    ├── ehr_service_pb2.py     # Generated message classes
    ├── ehr_service_pb2_grpc.py # Generated service classes
    └── ehr_service_pb2.pyi    # Type hints for generated code
```

### Regenerating Proto Files

If you modify the `.proto` file, regenerate the Python files:

```bash
cd proto
python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    --pyi_out=. \
    ehr_service.proto
```

## Error Handling

The API Gateway handles various error scenarios:

- **400 Bad Request**: Invalid input data
- **404 Not Found**: Patient not found
- **409 Conflict**: Patient already exists
- **500 Internal Server Error**: Server-side errors (including gRPC errors)

## Blood Types

Supported blood types:
- A+, A-, B+, B-, AB+, AB-, O+, O-

## Configuration

Edit the configuration constants in `main.py`:

```python
GRPC_HOST = 'localhost'  # gRPC server host
GRPC_PORT = 50051        # gRPC server port
```

## Advantages of this Architecture

1. **Separation of Concerns**: REST API layer separate from business logic
2. **Technology Flexibility**: Can replace backend without changing client API
3. **Performance**: gRPC is faster than REST for internal communication
4. **Type Safety**: Protocol Buffers provide strong typing
5. **Multiple Clients**: Same gRPC backend can serve multiple gateways (REST, GraphQL, etc.)
6. **Scalability**: Can scale API gateway and backend services independently

## Related Services

- **ehr-crud-service**: The gRPC backend service that handles database operations
