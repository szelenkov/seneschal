"""
Database models for Seneschal Python port.
Defines SQLAlchemy ORM models representing database structures.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass, field

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, Index, UniqueConstraint, CheckConstraint, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.types import TypeDecorator

Base = declarative_base()


class DataTypeCategory(Enum):
    """Categories for SQL data types"""
    INTEGER = "integer"
    REAL = "real"
    TEXT = "text"
    BINARY = "binary"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    OTHER = "other"


@dataclass
class ColumnDefault:
    """Represents a column default value"""
    type: str  # 'text', 'null', 'auto_increment', 'expression'
    value: Optional[str] = None


@dataclass
class ColumnConstraint:
    """Represents a column constraint"""
    name: str
    constraint_type: str  # 'primary_key', 'unique', 'check', 'foreign_key'
    definition: str


@dataclass
class TableColumn:
    """Represents a table column with full metadata"""
    name: str
    data_type: str
    allow_null: bool = True
    default: Optional[ColumnDefault] = None
    comment: Optional[str] = None
    charset: Optional[str] = None
    collation: Optional[str] = None
    is_unsigned: bool = False
    is_zerofill: bool = False
    is_invisible: bool = False
    is_virtual: bool = False
    generation_expression: Optional[str] = None
    srid: Optional[int] = None
    constraints: List[ColumnConstraint] = field(default_factory=list)


@dataclass
class TableKey:
    """Represents a table index or key"""
    name: str
    key_type: str  # 'PRIMARY', 'UNIQUE', 'KEY', 'FULLTEXT', 'SPATIAL'
    columns: List[str]
    algorithm: Optional[str] = None
    comment: Optional[str] = None
    is_primary: bool = False
    is_unique: bool = False


@dataclass
class ForeignKeyConstraint:
    """Represents a foreign key constraint"""
    name: str
    columns: List[str]
    referenced_table: str
    referenced_columns: List[str]
    on_delete: str = "RESTRICT"  # CASCADE, SET NULL, etc.
    on_update: str = "RESTRICT"


@dataclass
class TableDefinition:
    """Complete table definition"""
    name: str
    schema: str
    columns: List[TableColumn] = field(default_factory=list)
    keys: List[TableKey] = field(default_factory=list)
    foreign_keys: List[ForeignKeyConstraint] = field(default_factory=list)
    engine: Optional[str] = None
    charset: Optional[str] = None
    collation: Optional[str] = None
    comment: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class ViewDefinition:
    """View definition"""
    name: str
    schema: str
    definition_sql: str
    is_updatable: bool = False
    created_at: Optional[datetime] = None


@dataclass
class RoutineDefinition:
    """Stored procedure or function definition"""
    name: str
    schema: str
    routine_type: str  # 'PROCEDURE' or 'FUNCTION'
    definition_sql: str
    is_deterministic: bool = False
    sql_data_access: str = "MODIFIES SQL DATA"
    security_type: str = "INVOKER"
    created_at: Optional[datetime] = None


@dataclass
class TriggerDefinition:
    """Trigger definition"""
    name: str
    schema: str
    table_name: str
    trigger_event: str  # INSERT, UPDATE, DELETE
    trigger_time: str  # BEFORE, AFTER
    definition_sql: str
    created_at: Optional[datetime] = None


# Audit models for tracking changes
class AuditLog(Base):
    """Audit log for tracking database changes"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    operation = Column(String(50), nullable=False)  # CREATE, ALTER, DROP
    object_type = Column(String(50), nullable=False)  # TABLE, VIEW, PROCEDURE
    object_name = Column(String(255), nullable=False)
    old_definition = Column(Text)
    new_definition = Column(Text, nullable=False)
    user = Column(String(255))
    status = Column(String(20), default='SUCCESS')  # SUCCESS, FAILED
    error_message = Column(Text)
    
    __table_args__ = (
        Index('idx_timestamp', 'timestamp'),
        Index('idx_operation', 'operation'),
    )


class ConnectionProfile(Base):
    """Saved database connection profiles"""
    __tablename__ = 'connection_profiles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    database_type = Column(String(50), nullable=False)  # mysql, postgresql, mssql, sqlite
    host = Column(String(255))
    port = Column(Integer)
    database = Column(String(255))
    username = Column(String(255))
    password_encrypted = Column(String(512))  # Encrypted
    charset = Column(String(50), default='utf8mb4')
    ssl_enabled = Column(Boolean, default=False)
    ssh_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(datetime.timezone.utc))
    modified_at = Column(DateTime, default=datetime.now(datetime.timezone.utc),
                         onupdate=datetime.now(datetime.timezone.utc))
    
    __table_args__ = (
        Index('idx_name', 'name'),
        Index('idx_database_type', 'database_type'),
    )


class QueryHistory(Base):
    """Query history for quick access to recent queries"""
    __tablename__ = 'query_history'
    
    id = Column(Integer, primary_key=True)
    connection_profile_id = Column(Integer, ForeignKey('connection_profiles.id'))
    query_text = Column(Text, nullable=False)
    result_count = Column(Integer)
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_favorite = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('idx_connection', 'connection_profile_id'),
        Index('idx_created_at', 'created_at'),
    )

