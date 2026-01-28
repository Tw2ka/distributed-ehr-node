# Distributed EHR Node - API Gateway Setup Complete

## What Was Created

### 1. FastAPI REST API Gateway (`api-gateway-service/`)

A complete REST API gateway service that:
- Exposes RESTful endpoints for patient CRUD operations
- Communicates with the gRPC backend service
- Handles request/response validation using Pydantic models
- Provides automatic API documentation (Swagger UI & ReDoc)

### 2. Key Files Created

#### **main.py**
- FastAPI application with full CRUD endpoints
- Endpoints:
  - `POST /patients` - Create patient
  - `GET /patients/{patient_uuid}` - Get patient by UUID
  - `GET /patients` - List all patients (paginated)
  - `GET /patients/search/{patient_id}` - Search by patient_id
  - `PUT /patients/{patient_uuid}` - Full update
  - `PATCH /patients/{patient_uuid}` - Partial update
  - `DELETE /patients/{patient_uuid}` - Delete patient

#### **models.py**
- `BloodType` enum (A+, A-, B+, B-, AB+, AB-, O+, O-)
- `PatientCreate` - Request model for creating patients
- `PatientUpdate` - Request model for updating patients (all fields optional)
- `PatientResponse` - Response model with UUID and timestamps
- `DeleteResponse` - Response model for delete operations
- `ErrorResponse` - Error response model

#### **grpc_client.py**
- Async gRPC client wrapper with context manager
- Handles translation between REST models and gRPC messages
- Blood type enum conversion between API and protobuf
- Methods matching all gRPC service operations

#### **proto/ directory**
- `ehr_service.proto` - Protocol Buffer definition (copied from ehr-crud-service)
- `ehr_service_pb2.py` - Generated message classes
- `ehr_service_pb2_grpc.py` - Generated service/stub classes
- `ehr_service_pb2.pyi` - Type hints for IDE support
- `__init__.py` - Makes proto a Python package

#### **Supporting Files**
- `requirements.txt` - Python dependencies
- `README.md` - Comprehensive documentation
- `start.ps1` - PowerShell startup script

## Understanding pb2 and pb2_grpc

### **What are they?**

These are auto-generated Python files from the Protocol Buffer (`.proto`) definition:

#### **ehr_service_pb2.py** (pb2 = Protocol Buffer 2)
- Contains Python classes for all message types
- Examples: `PatientMessage`, `CreatePatientRequest`, `PatientResponse`
- Contains enum definitions: `BloodType` enum values
- Handles serialization/deserialization
- Think of it as: **Data structures and schemas**

#### **ehr_service_pb2_grpc.py** (pb2_grpc = Protocol Buffer 2 + gRPC)
- Contains gRPC service classes
- `EhrServiceStub` - Client for making RPC calls
- `EhrServiceServicer` - Server base class for implementing service
- Helper functions for server registration
- Think of it as: **Communication layer and RPC methods**

### **Why Both?**

They serve different purposes:

| File | Purpose | Analogy |
|------|---------|---------|
| pb2.py | Data structures, messages | JSON schemas + data classes |
| pb2_grpc.py | RPC methods, client/server | HTTP client + route handlers |

```python
# pb2 provides the data structures
request = ehr_service_pb2.CreatePatientRequest(...)  # From pb2

# pb2_grpc provides the communication
stub = ehr_service_pb2_grpc.EhrServiceStub(channel)  # From pb2_grpc
response = await stub.CreatePatient(request)         # Method from pb2_grpc, data from pb2
```

### **Do You Need Both?**

**YES!** You need both files because:
- **pb2.py** - To create and work with messages
- **pb2_grpc.py** - To make RPC calls
- They work together - pb2_grpc methods use pb2 messages as parameters and return types

### **How Were They Created?**

```bash
python -m grpc_tools.protoc \
    -I. \
    --python_out=. \      # Generates pb2.py
    --grpc_python_out=. \  # Generates pb2_grpc.py
    --pyi_out=. \         # Generates .pyi for type hints
    ehr_service.proto
```

**DO NOT EDIT** these files manually! Regenerate them when the `.proto` file changes.

## Architecture Flow

```
┌─────────────────┐
│   REST Client   │
│  (Browser/App)  │
└────────┬────────┘
         │ HTTP/REST
         │ (JSON)
         ▼
┌─────────────────────────┐
│   API Gateway Service   │
│      (FastAPI)          │
│  ┌──────────────────┐   │
│  │    main.py       │   │  Handles HTTP requests
│  │    models.py     │   │  Validates data
│  │ grpc_client.py   │   │  Translates to gRPC
│  └──────────────────┘   │
└────────┬────────────────┘
         │ gRPC
         │ (Protobuf)
         ▼
┌─────────────────────────┐
│  EHR CRUD Service       │
│     (gRPC Server)       │
│  ┌──────────────────┐   │
│  │ grpc_server.py   │   │  Handles gRPC calls
│  │ crud_service.py  │   │  Business logic
│  │   database.py    │   │  DB operations
│  └──────────────────┘   │
└────────┬────────────────┘
         │
         ▼
    ┌──────────┐
    │ MongoDB  │
    └──────────┘
```

## Running the System

### Step 1: Start MongoDB
```bash
# Make sure MongoDB is running
mongod
```

### Step 2: Start gRPC Server
```bash
cd ehr-crud-service
python grpc_server.py
```

### Step 3: Start API Gateway
```bash
cd api-gateway-service
.\start.ps1
# Or manually:
# uvicorn main:app --reload --port 8000
```

### Step 4: Access the API
- API Base: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing the API

### Using Swagger UI
1. Open http://localhost:8000/docs
2. Try the endpoints interactively
3. See request/response schemas

### Using cURL

```bash
# Create a patient
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

# Get all patients
curl "http://localhost:8000/patients"

# Get patient by UUID
curl "http://localhost:8000/patients/{uuid}"

# Update patient
curl -X PUT "http://localhost:8000/patients/{uuid}" \
  -H "Content-Type: application/json" \
  -d '{"diagnosis": "Updated", "weight": 72}'

# Delete patient
curl -X DELETE "http://localhost:8000/patients/{uuid}"
```

## Key Features

### 1. REST to gRPC Translation
- REST API accepts JSON
- Converts to Protocol Buffer messages
- Calls gRPC service
- Converts response back to JSON

### 2. Type Safety
- Pydantic models validate REST API requests/responses
- Protocol Buffers validate gRPC messages
- Type hints throughout the code

### 3. Error Handling
- HTTP status codes (400, 404, 409, 500)
- Translates gRPC errors to HTTP errors
- Clear error messages

### 4. Documentation
- Auto-generated Swagger UI
- Auto-generated ReDoc
- Request/response examples

### 5. Async/Await
- Non-blocking I/O
- Better performance under load
- Efficient resource usage

## Benefits of This Architecture

1. **Separation of Concerns**
   - API layer separate from business logic
   - Can change frontend without changing backend

2. **Technology Flexibility**
   - REST for external clients (web/mobile apps)
   - gRPC for internal microservices (fast & efficient)

3. **Scalability**
   - Scale API gateway and backend independently
   - Multiple gateways can connect to same backend

4. **Performance**
   - gRPC is faster than REST for internal communication
   - Protocol Buffers are smaller than JSON
   - Binary serialization is faster

5. **Maintainability**
   - Clear separation of layers
   - Well-documented APIs
   - Type-safe code

## Troubleshooting

### "Cannot find reference 'A_POSITIVE'"
- This means the proto files haven't been generated or imported correctly
- Make sure `ehr_service_pb2.py` and `ehr_service_pb2_grpc.py` exist in the `proto/` directory
- Make sure `proto/__init__.py` exists
- Try regenerating: `python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. --pyi_out=. ehr_service.proto`

### "Connection refused" when calling API
- Make sure the gRPC server is running on localhost:50051
- Check `GRPC_HOST` and `GRPC_PORT` in main.py

### Import errors
- Install dependencies: `pip install -r requirements.txt`
- Make sure you're in the correct directory

## Next Steps

1. **Add Authentication**: Implement JWT or API key authentication
2. **Add Rate Limiting**: Prevent API abuse
3. **Add Caching**: Cache frequently accessed data
4. **Add Logging**: Implement structured logging
5. **Add Monitoring**: Add metrics and health checks
6. **Add Tests**: Write unit and integration tests
7. **Dockerize**: Create Docker containers for easy deployment

## Summary

You now have a complete REST API Gateway that:
- ✅ Provides RESTful endpoints for patient CRUD operations
- ✅ Communicates with the gRPC backend service using Protocol Buffers
- ✅ Includes pb2 (data structures) and pb2_grpc (RPC methods) files
- ✅ Validates requests/responses with Pydantic models
- ✅ Provides automatic API documentation
- ✅ Handles errors appropriately
- ✅ Is fully async for better performance
- ✅ Is well-documented and ready to use

The pb2 and pb2_grpc files work together to enable gRPC communication - pb2 provides the message structures, and pb2_grpc provides the service methods. Both are essential and auto-generated from the .proto file.
