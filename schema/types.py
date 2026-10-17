import uuid
from datetime import datetime

from sqlalchemy import TypeDecorator
from sqlalchemy.dialects.postgresql import (
    UUID as PG_UUID,
    JSONB as PG_JSONB
)
from sqlalchemy.types import (
    String,
    JSON as DefaultJSON
)

__all__ = ["MappedUUID", "MappedJSON"]

class MappedUUID(TypeDecorator):
    """
    Use the postgresql native UUID type if available,
    otherwise falls back to a String(36) representation for SQLite
    """
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value if isinstance(value, uuid.UUID) else uuid.UUID(value)
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(value) if not isinstance(value, uuid.UUID) else value

class MappedJSON(TypeDecorator):
    """
    Use the postgresql native JSONB type if available,
    otherwise falls back to a JSON representation for SQLite
    """
    impl = DefaultJSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_JSONB())
        else:
            return dialect.type_descriptor(DefaultJSON())
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return value
