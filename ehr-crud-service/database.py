from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class DatabaseSettings(BaseSettings):
    """Database configuration using Pydantic"""
    mongodb_url: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URL")
    database_name: str = Field(default="ehr_database", alias="DATABASE_NAME")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create settings instance
settings = DatabaseSettings()


class Database:
    client: Optional[AsyncIOMotorClient] = None

    @classmethod
    async def initialize(cls):
        from models import Patient

        if cls.client is None:
            cls.client = AsyncIOMotorClient(settings.mongodb_url)

        await init_beanie(
            database=cls.client[settings.database_name],
            document_models=[Patient]
        )

    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        if cls.client is None:
            cls.client = AsyncIOMotorClient(settings.mongodb_url)
        return cls.client

    @classmethod
    def get_database(cls):
        client = cls.get_client()
        return client[settings.database_name]

    @classmethod
    async def close_connection(cls):
        if cls.client is not None:
            cls.client.close()
            cls.client = None


def get_patient_collection():
    db = Database.get_database()
    return db["patients"]
