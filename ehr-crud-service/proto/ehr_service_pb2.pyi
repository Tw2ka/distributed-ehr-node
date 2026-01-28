from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BloodType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BLOOD_TYPE_UNSPECIFIED: _ClassVar[BloodType]
    A_POSITIVE: _ClassVar[BloodType]
    A_NEGATIVE: _ClassVar[BloodType]
    B_POSITIVE: _ClassVar[BloodType]
    B_NEGATIVE: _ClassVar[BloodType]
    AB_POSITIVE: _ClassVar[BloodType]
    AB_NEGATIVE: _ClassVar[BloodType]
    O_POSITIVE: _ClassVar[BloodType]
    O_NEGATIVE: _ClassVar[BloodType]
BLOOD_TYPE_UNSPECIFIED: BloodType
A_POSITIVE: BloodType
A_NEGATIVE: BloodType
B_POSITIVE: BloodType
B_NEGATIVE: BloodType
AB_POSITIVE: BloodType
AB_NEGATIVE: BloodType
O_POSITIVE: BloodType
O_NEGATIVE: BloodType

class PatientMessage(_message.Message):
    __slots__ = ("id", "patient_id", "name", "birth_date", "height", "weight", "blood_type", "diagnosis", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    PATIENT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BIRTH_DATE_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    BLOOD_TYPE_FIELD_NUMBER: _ClassVar[int]
    DIAGNOSIS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    patient_id: str
    name: str
    birth_date: str
    height: int
    weight: int
    blood_type: BloodType
    diagnosis: str
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[str] = ..., patient_id: _Optional[str] = ..., name: _Optional[str] = ..., birth_date: _Optional[str] = ..., height: _Optional[int] = ..., weight: _Optional[int] = ..., blood_type: _Optional[_Union[BloodType, str]] = ..., diagnosis: _Optional[str] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class CreatePatientRequest(_message.Message):
    __slots__ = ("patient_id", "name", "birth_date", "height", "weight", "blood_type", "diagnosis")
    PATIENT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BIRTH_DATE_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    BLOOD_TYPE_FIELD_NUMBER: _ClassVar[int]
    DIAGNOSIS_FIELD_NUMBER: _ClassVar[int]
    patient_id: str
    name: str
    birth_date: str
    height: int
    weight: int
    blood_type: BloodType
    diagnosis: str
    def __init__(self, patient_id: _Optional[str] = ..., name: _Optional[str] = ..., birth_date: _Optional[str] = ..., height: _Optional[int] = ..., weight: _Optional[int] = ..., blood_type: _Optional[_Union[BloodType, str]] = ..., diagnosis: _Optional[str] = ...) -> None: ...

class GetPatientRequest(_message.Message):
    __slots__ = ("patient_uuid",)
    PATIENT_UUID_FIELD_NUMBER: _ClassVar[int]
    patient_uuid: str
    def __init__(self, patient_uuid: _Optional[str] = ...) -> None: ...

class GetAllPatientsRequest(_message.Message):
    __slots__ = ("skip", "limit")
    SKIP_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    skip: int
    limit: int
    def __init__(self, skip: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class SearchPatientByIdRequest(_message.Message):
    __slots__ = ("patient_id",)
    PATIENT_ID_FIELD_NUMBER: _ClassVar[int]
    patient_id: str
    def __init__(self, patient_id: _Optional[str] = ...) -> None: ...

class UpdatePatientRequest(_message.Message):
    __slots__ = ("patient_uuid", "patient_id", "name", "birth_date", "height", "weight", "blood_type", "diagnosis")
    PATIENT_UUID_FIELD_NUMBER: _ClassVar[int]
    PATIENT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BIRTH_DATE_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    BLOOD_TYPE_FIELD_NUMBER: _ClassVar[int]
    DIAGNOSIS_FIELD_NUMBER: _ClassVar[int]
    patient_uuid: str
    patient_id: str
    name: str
    birth_date: str
    height: int
    weight: int
    blood_type: BloodType
    diagnosis: str
    def __init__(self, patient_uuid: _Optional[str] = ..., patient_id: _Optional[str] = ..., name: _Optional[str] = ..., birth_date: _Optional[str] = ..., height: _Optional[int] = ..., weight: _Optional[int] = ..., blood_type: _Optional[_Union[BloodType, str]] = ..., diagnosis: _Optional[str] = ...) -> None: ...

class DeletePatientRequest(_message.Message):
    __slots__ = ("patient_uuid",)
    PATIENT_UUID_FIELD_NUMBER: _ClassVar[int]
    patient_uuid: str
    def __init__(self, patient_uuid: _Optional[str] = ...) -> None: ...

class PatientResponse(_message.Message):
    __slots__ = ("patient",)
    PATIENT_FIELD_NUMBER: _ClassVar[int]
    patient: PatientMessage
    def __init__(self, patient: _Optional[_Union[PatientMessage, _Mapping]] = ...) -> None: ...

class GetAllPatientsResponse(_message.Message):
    __slots__ = ("patients",)
    PATIENTS_FIELD_NUMBER: _ClassVar[int]
    patients: _containers.RepeatedCompositeFieldContainer[PatientMessage]
    def __init__(self, patients: _Optional[_Iterable[_Union[PatientMessage, _Mapping]]] = ...) -> None: ...

class DeletePatientResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...
