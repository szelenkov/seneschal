"""
Database provider abstraction layer.
Implements dialect-specific SQL generation and schema retrieval.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass

from .models import (
    TableColumn, TableKey, TableDefinition, ViewDefinition,
    RoutineDefinition, TriggerDefinition, ForeignKeyConstraint,
    ColumnDefault, DataTypeCategory
)


class QueryTemplateId(Enum):
    """Query template identifiers for provider-specific SQL generation"""
    # Database queries
    DATABASE_TABLE = "database_table"
    DATABASE_TABLE_ID = "database_table_id"
    DATABASE_DROP = "database_drop"
    
    # Object queries
    DBOBJECTS_TABLE = "dbobjects_table"
    DBOBJECTS_CREATE_COL = "dbobjects_create_col"
    DBOBJECTS_UPDATE_COL = "dbobjects_update_col"
    DBOBJECTS_TYPE_COL = "dbobjects_type_col"
    
    # Schema queries
    GET_TABLE_COLUMNS = "get_table_columns"
    GET_TABLE_KEYS = "get_table_keys"
    GET_FOREIGN_KEYS = "get_foreign_keys"
    GET_VIEWS = "get_views"
    GET_PROCEDURES = "get_procedures"
    GET_FUNCTIONS = "get_functions"
    GET_TRIGGERS = "get_triggers"
    GET_EVENTS = "get_events"
    
    # Row count queries
    GET_ROW_COUNT_EXACT = "get_row_count_exact"
    GET_ROW_COUNT_APPROX = "get_row_count_approx"
    
    # Utility queries
    CURRENT_USER_HOST = "current_user_host"
    USE_QUERY = "use_query"
    KILL_QUERY = "kill_query"
    EXPLAIN = "explain"
    SHOW_WARNINGS = "show_warnings"
    
    # Session variables
    GLOBAL_VARIABLES = "global_variables"
    SESSION_VARIABLES = "session_variables"
    GLOBAL_STATUS = "global_status"
    COMMANDS_COUNTERS = "commands_counters"


@dataclass
class DataTypeMapping:
    """Maps between database vendor types and normalized types"""
    native_name: str
    normalized_name: str
    category: DataTypeCategory
    has_length: bool = False
    has_precision: bool = False
    is_numeric: bool = False
    is_text: bool = False
    is_binary: bool = False
    is_temporal: bool = False


class DatabaseProvider(ABC):
    """Abstract base class for database provider implementations"""
    
    def __init__(self, server_version: int = 0):
        self.server_version = server_version
        self._query_templates: Dict[QueryTemplateId, str] = {}
        self._data_type_map: Dict[str, DataTypeMapping] = {}
        self._initialize_templates()
        self._initialize_data_types()
    
    @abstractmethod
    def _initialize_templates(self) -> None:
        """Initialize SQL query templates for this provider"""
        pass
    
    @abstractmethod
    def _initialize_data_types(self) -> None:
        """Initialize data type mappings for this provider"""
        pass
    
    @abstractmethod
    async def connect(self, **connection_params) -> Any:
        """Create database connection"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection"""
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, params: Optional[List] = None) -> Any:
        """Execute a query and return results"""
        pass
    
    @abstractmethod
    async def execute_update(self, query: str, params: Optional[List] = None) -> int:
        """Execute an update/insert/delete and return affected rows"""
        pass
    
    @abstractmethod
    async def get_databases(self) -> List[str]:
        """Get list of available databases"""
        pass
    
    @abstractmethod
    async def get_tables(self, database: str) -> List[str]:
        """Get list of tables in a database"""
        pass
    
    @abstractmethod
    async def get_views(self, database: str) -> List[str]:
        """Get list of views in a database"""
        pass
    
    @abstractmethod
    async def get_procedures(self, database: str) -> List[str]:
        """Get list of stored procedures in a database"""
        pass
    
    @abstractmethod
    async def get_functions(self, database: str) -> List[str]:
        """Get list of stored functions in a database"""
        pass
    
    @abstractmethod
    async def get_triggers(self, database: str, table: Optional[str] = None) -> List[str]:
        """Get list of triggers"""
        pass
    
    @abstractmethod
    async def get_table_definition(self, database: str, table: str) -> TableDefinition:
        """Get complete table definition including columns, keys, constraints"""
        pass
    
    @abstractmethod
    async def get_view_definition(self, database: str, view: str) -> ViewDefinition:
        """Get view SQL definition"""
        pass
    
    @abstractmethod
    async def get_procedure_definition(self, database: str, procedure: str) -> RoutineDefinition:
        """Get procedure SQL definition"""
        pass
    
    @abstractmethod
    async def get_function_definition(self, database: str, function: str) -> RoutineDefinition:
        """Get function SQL definition"""
        pass
    
    @abstractmethod
    async def get_trigger_definition(self, database: str, trigger: str) -> TriggerDefinition:
        """Get trigger SQL definition"""
        pass
    
    @abstractmethod
    async def get_row_count(self, database: str, table: str, exact: bool = False) -> int:
        """Get row count for a table"""
        pass
    
    @abstractmethod
    def get_query_template(self, template_id: QueryTemplateId) -> Optional[str]:
        """Get SQL template for a query type"""
        pass
    
    @abstractmethod
    def format_identifier(self, identifier: str) -> str:
        """Format an identifier (table name, column name) for this database"""
        pass
    
    @abstractmethod
    def format_value(self, value: Any, datatype: str) -> str:
        """Format a value for SQL based on its type"""
        pass
    
    def get_data_type_mapping(self, native_type: str) -> Optional[DataTypeMapping]:
        """Get normalized data type mapping"""
        return self._data_type_map.get(native_type.upper())
    
    def supports_query_template(self, template_id: QueryTemplateId) -> bool:
        """Check if this provider supports a particular query template"""
        return template_id in self._query_templates


class MySQLProvider(DatabaseProvider):
    """MySQL/MariaDB provider implementation"""
    
    def _initialize_templates(self) -> None:
        """Initialize MySQL query templates"""
        self._query_templates = {
            QueryTemplateId.DATABASE_TABLE: "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA",
            QueryTemplateId.GET_TABLE_COLUMNS: 
                "SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, "
                "COLUMN_COMMENT, CHARACTER_SET_NAME, COLLATION_NAME FROM "
                "INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
                "ORDER BY ORDINAL_POSITION",
            QueryTemplateId.GET_ROW_COUNT_EXACT: "SELECT COUNT(*) FROM `{schema}`.`{table}`",
            QueryTemplateId.GET_ROW_COUNT_APPROX: "SELECT TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s",
            QueryTemplateId.USE_QUERY: "USE `{database}`",
            QueryTemplateId.CURRENT_USER_HOST: "SELECT CONCAT(USER(), ' at ', @@hostname)",
            QueryTemplateId.EXPLAIN: "EXPLAIN {query}",
        }
    
    def _initialize_data_types(self) -> None:
        """Initialize MySQL data type mappings"""
        self._data_type_map = {
            'TINYINT': DataTypeMapping('TINYINT', 'TINYINT', DataTypeCategory.INTEGER, is_numeric=True),
            'SMALLINT': DataTypeMapping('SMALLINT', 'SMALLINT', DataTypeCategory.INTEGER, is_numeric=True),
            'MEDIUMINT': DataTypeMapping('MEDIUMINT', 'MEDIUMINT', DataTypeCategory.INTEGER, is_numeric=True),
            'INT': DataTypeMapping('INT', 'INT', DataTypeCategory.INTEGER, is_numeric=True),
            'INTEGER': DataTypeMapping('INTEGER', 'INT', DataTypeCategory.INTEGER, is_numeric=True),
            'BIGINT': DataTypeMapping('BIGINT', 'BIGINT', DataTypeCategory.INTEGER, is_numeric=True),
            'FLOAT': DataTypeMapping('FLOAT', 'FLOAT', DataTypeCategory.REAL, has_precision=True, is_numeric=True),
            'DOUBLE': DataTypeMapping('DOUBLE', 'DOUBLE', DataTypeCategory.REAL, has_precision=True, is_numeric=True),
            'DECIMAL': DataTypeMapping('DECIMAL', 'DECIMAL', DataTypeCategory.REAL, has_precision=True, is_numeric=True),
            'CHAR': DataTypeMapping('CHAR', 'CHAR', DataTypeCategory.TEXT, has_length=True, is_text=True),
            'VARCHAR': DataTypeMapping('VARCHAR', 'VARCHAR', DataTypeCategory.TEXT, has_length=True, is_text=True),
            'TEXT': DataTypeMapping('TEXT', 'TEXT', DataTypeCategory.TEXT, is_text=True),
            'TINYTEXT': DataTypeMapping('TINYTEXT', 'TINYTEXT', DataTypeCategory.TEXT, is_text=True),
            'MEDIUMTEXT': DataTypeMapping('MEDIUMTEXT', 'MEDIUMTEXT', DataTypeCategory.TEXT, is_text=True),
            'LONGTEXT': DataTypeMapping('LONGTEXT', 'LONGTEXT', DataTypeCategory.TEXT, is_text=True),
            'BLOB': DataTypeMapping('BLOB', 'BLOB', DataTypeCategory.BINARY, is_binary=True),
            'TINYBLOB': DataTypeMapping('TINYBLOB', 'TINYBLOB', DataTypeCategory.BINARY, is_binary=True),
            'MEDIUMBLOB': DataTypeMapping('MEDIUMBLOB', 'MEDIUMBLOB', DataTypeCategory.BINARY, is_binary=True),
            'LONGBLOB': DataTypeMapping('LONGBLOB', 'LONGBLOB', DataTypeCategory.BINARY, is_binary=True),
            'DATE': DataTypeMapping('DATE', 'DATE', DataTypeCategory.TEMPORAL, is_temporal=True),
            'TIME': DataTypeMapping('TIME', 'TIME', DataTypeCategory.TEMPORAL, is_temporal=True),
            'DATETIME': DataTypeMapping('DATETIME', 'DATETIME', DataTypeCategory.TEMPORAL, is_temporal=True),
            'TIMESTAMP': DataTypeMapping('TIMESTAMP', 'TIMESTAMP', DataTypeCategory.TEMPORAL, is_temporal=True),
            'YEAR': DataTypeMapping('YEAR', 'YEAR', DataTypeCategory.TEMPORAL, is_temporal=True),
            'JSON': DataTypeMapping('JSON', 'JSON', DataTypeCategory.OTHER),
            'ENUM': DataTypeMapping('ENUM', 'ENUM', DataTypeCategory.OTHER, has_length=True),
            'SET': DataTypeMapping('SET', 'SET', DataTypeCategory.OTHER, has_length=True),
            'BOOLEAN': DataTypeMapping('BOOLEAN', 'BOOLEAN', DataTypeCategory.OTHER, is_numeric=True),
            'GEOMETRY': DataTypeMapping('GEOMETRY', 'GEOMETRY', DataTypeCategory.SPATIAL),
            'POINT': DataTypeMapping('POINT', 'POINT', DataTypeCategory.SPATIAL),
        }
    
    async def connect(self, **connection_params) -> Any:
        """Create MySQL connection"""
        raise NotImplementedError("Use SQLAlchemy engine instead")
    
    async def disconnect(self) -> None:
        """Close connection"""
        pass
    
    async def execute_query(self, query: str, params: Optional[List] = None) -> Any:
        """Execute a query"""
        raise NotImplementedError("Use SQLAlchemy engine instead")
    
    async def execute_update(self, query: str, params: Optional[List] = None) -> int:
        """Execute an update"""
        raise NotImplementedError("Use SQLAlchemy engine instead")
    
    async def get_databases(self) -> List[str]:
        """Get list of MySQL databases"""
        raise NotImplementedError("Implement with SQLAlchemy engine")
    
    async def get_tables(self, database: str) -> List[str]:
        """Get tables from database"""
        raise NotImplementedError("Implement with SQLAlchemy inspector")
    
    async def get_views(self, database: str) -> List[str]:
        """Get views from database"""
        raise NotImplementedError("Implement with SQLAlchemy inspector")
    
    async def get_procedures(self, database: str) -> List[str]:
        """Get procedures from database"""
        raise NotImplementedError("Implement with SQLAlchemy")
    
    async def get_functions(self, database: str) -> List[str]:
        """Get functions from database"""
        raise NotImplementedError("Implement with SQLAlchemy")
    
    async def get_triggers(self, database: str, table: Optional[str] = None) -> List[str]:
        """Get triggers"""
        raise NotImplementedError("Implement with custom query")
    
    async def get_table_definition(self, database: str, table: str) -> TableDefinition:
        """Get table definition"""
        raise NotImplementedError("Implement with SQLAlchemy inspector")
    
    async def get_view_definition(self, database: str, view: str) -> ViewDefinition:
        """Get view definition"""
        raise NotImplementedError("Implement with SHOW CREATE VIEW")
    
    async def get_procedure_definition(self, database: str, procedure: str) -> RoutineDefinition:
        """Get procedure definition"""
        raise NotImplementedError("Implement with SHOW CREATE PROCEDURE")
    
    async def get_function_definition(self, database: str, function: str) -> RoutineDefinition:
        """Get function definition"""
        raise NotImplementedError("Implement with SHOW CREATE FUNCTION")
    
    async def get_trigger_definition(self, database: str, trigger: str) -> TriggerDefinition:
        """Get trigger definition"""
        raise NotImplementedError("Implement with SHOW CREATE TRIGGER")
    
    async def get_row_count(self, database: str, table: str, exact: bool = False) -> int:
        """Get row count for MySQL table"""
        raise NotImplementedError("Implement with custom query")
    
    def get_query_template(self, template_id: QueryTemplateId) -> Optional[str]:
        """Get MySQL query template"""
        return self._query_templates.get(template_id)
    
    def format_identifier(self, identifier: str) -> str:
        """Format MySQL identifier with backticks"""
        return f"`{identifier.replace(chr(96), chr(96)*2)}`"
    
    def format_value(self, value: Any, datatype: str) -> str:
        """Format value for MySQL"""
        if value is None:
            return "NULL"
        if datatype.upper() in ['INT', 'BIGINT', 'SMALLINT', 'TINYINT', 'MEDIUMINT']:
            return str(value)
        if datatype.upper() in ['FLOAT', 'DOUBLE', 'DECIMAL']:
            return str(value)
        if datatype.upper() in ['DATE', 'TIME', 'DATETIME', 'TIMESTAMP']:
            return f"'{value}'"
        # String types
        return f"'{str(value).replace(chr(39), chr(39)*2)}'"


class PostgreSQLProvider(DatabaseProvider):
    """PostgreSQL provider implementation"""
    
    def _initialize_templates(self) -> None:
        """Initialize PostgreSQL query templates"""
        self._query_templates = {
            QueryTemplateId.DATABASE_TABLE: "SELECT datname FROM pg_database WHERE datistemplate = false",
            QueryTemplateId.GET_TABLE_COLUMNS:
                "SELECT column_name, data_type, is_nullable, column_default FROM "
                "information_schema.columns WHERE table_schema = %s AND table_name = %s "
                "ORDER BY ordinal_position",
        }
    
    def _initialize_data_types(self) -> None:
        """Initialize PostgreSQL data type mappings"""
        self._data_type_map = {
            'SMALLINT': DataTypeMapping('SMALLINT', 'SMALLINT', DataTypeCategory.INTEGER, is_numeric=True),
            'INTEGER': DataTypeMapping('INTEGER', 'INTEGER', DataTypeCategory.INTEGER, is_numeric=True),
            'BIGINT': DataTypeMapping('BIGINT', 'BIGINT', DataTypeCategory.INTEGER, is_numeric=True),
            'DECIMAL': DataTypeMapping('DECIMAL', 'DECIMAL', DataTypeCategory.REAL, has_precision=True, is_numeric=True),
            'NUMERIC': DataTypeMapping('NUMERIC', 'NUMERIC', DataTypeCategory.REAL, has_precision=True, is_numeric=True),
            'REAL': DataTypeMapping('REAL', 'REAL', DataTypeCategory.REAL, is_numeric=True),
            'DOUBLE PRECISION': DataTypeMapping('DOUBLE PRECISION', 'DOUBLE', DataTypeCategory.REAL, is_numeric=True),
            'CHARACTER': DataTypeMapping('CHARACTER', 'CHAR', DataTypeCategory.TEXT, has_length=True, is_text=True),
            'VARCHAR': DataTypeMapping('VARCHAR', 'VARCHAR', DataTypeCategory.TEXT, has_length=True, is_text=True),
            'TEXT': DataTypeMapping('TEXT', 'TEXT', DataTypeCategory.TEXT, is_text=True),
            'BYTEA': DataTypeMapping('BYTEA', 'BYTEA', DataTypeCategory.BINARY, is_binary=True),
            'DATE': DataTypeMapping('DATE', 'DATE', DataTypeCategory.TEMPORAL, is_temporal=True),
            'TIME': DataTypeMapping('TIME', 'TIME', DataTypeCategory.TEMPORAL, is_temporal=True),
            'TIMESTAMP': DataTypeMapping('TIMESTAMP', 'TIMESTAMP', DataTypeCategory.TEMPORAL, is_temporal=True),
            'JSON': DataTypeMapping('JSON', 'JSON', DataTypeCategory.OTHER),
            'JSONB': DataTypeMapping('JSONB', 'JSONB', DataTypeCategory.OTHER),
            'UUID': DataTypeMapping('UUID', 'UUID', DataTypeCategory.OTHER),
        }
    
    async def connect(self, **connection_params) -> Any:
        raise NotImplementedError("Use SQLAlchemy engine instead")
    
    async def disconnect(self) -> None:
        pass
    
    async def execute_query(self, query: str, params: Optional[List] = None) -> Any:
        raise NotImplementedError("Use SQLAlchemy engine instead")
    
    async def execute_update(self, query: str, params: Optional[List] = None) -> int:
        raise NotImplementedError("Use SQLAlchemy engine instead")
    
    async def get_databases(self) -> List[str]:
        raise NotImplementedError("Implement with SQLAlchemy engine")
    
    async def get_tables(self, database: str) -> List[str]:
        raise NotImplementedError("Implement with SQLAlchemy inspector")
    
    async def get_views(self, database: str) -> List[str]:
        raise NotImplementedError("Implement with SQLAlchemy inspector")
    
    async def get_procedures(self, database: str) -> List[str]:
        raise NotImplementedError("Implement with SQLAlchemy")
    
    async def get_functions(self, database: str) -> List[str]:
        raise NotImplementedError("Implement with SQLAlchemy")
    
    async def get_triggers(self, database: str, table: Optional[str] = None) -> List[str]:
        raise NotImplementedError("Implement with custom query")
    
    async def get_table_definition(self, database: str, table: str) -> TableDefinition:
        raise NotImplementedError("Implement with SQLAlchemy inspector")
    
    async def get_view_definition(self, database: str, view: str) -> ViewDefinition:
        raise NotImplementedError("Implement with custom query")
    
    async def get_procedure_definition(self, database: str, procedure: str) -> RoutineDefinition:
        raise NotImplementedError("Implement with custom query")
    
    async def get_function_definition(self, database: str, function: str) -> RoutineDefinition:
        raise NotImplementedError("Implement with custom query")
    
    async def get_trigger_definition(self, database: str, trigger: str) -> TriggerDefinition:
        raise NotImplementedError("Implement with custom query")
    
    async def get_row_count(self, database: str, table: str, exact: bool = False) -> int:
        raise NotImplementedError("Implement with custom query")
    
    def get_query_template(self, template_id: QueryTemplateId) -> Optional[str]:
        return self._query_templates.get(template_id)
    
    def format_identifier(self, identifier: str) -> str:
        """Format PostgreSQL identifier with double quotes"""
        return f'"{identifier.replace(chr(34), chr(34)*2)}"'
    
    def format_value(self, value: Any, datatype: str) -> str:
        """Format value for PostgreSQL"""
        if value is None:
            return "NULL"
        if 'INT' in datatype.upper():
            return str(value)
        if 'FLOAT' in datatype.upper() or 'NUMERIC' in datatype.upper() or 'DECIMAL' in datatype.upper():
            return str(value)
        if 'DATE' in datatype.upper() or 'TIME' in datatype.upper():
            return f"'{value}'"
        return f"'{str(value).replace(chr(39), chr(39)*2)}'"


class MSSQLProvider(DatabaseProvider):
    """Microsoft SQL Server provider implementation"""
    
    def _initialize_templates(self) -> None:
        """Initialize MSSQL query templates"""
        self._query_templates = {
            QueryTemplateId.DATABASE_TABLE: "SELECT name FROM sys.databases WHERE name NOT IN ('master', 'model', 'msdb', 'tempdb')",
        }
    
    def _initialize_data_types(self) -> None:
        """Initialize MSSQL data type mappings"""
        self._data_type_map = {
            'TINYINT': DataTypeMapping('TINYINT', 'TINYINT', DataTypeCategory.INTEGER, is_numeric=True),
            'SMALLINT': DataTypeMapping('SMALLINT', 'SMALLINT', DataTypeCategory.INTEGER, is_numeric=True),
            'INT': DataTypeMapping('INT', 'INT', DataTypeCategory.INTEGER, is_numeric=True),
            'BIGINT': DataTypeMapping('BIGINT', 'BIGINT', DataTypeCategory.INTEGER, is_numeric=True),
            'FLOAT': DataTypeMapping('FLOAT', 'FLOAT', DataTypeCategory.REAL, has_precision=True, is_numeric=True),
            'REAL': DataTypeMapping('REAL', 'REAL', DataTypeCategory.REAL, is_numeric=True),
            'DECIMAL': DataTypeMapping('DECIMAL', 'DECIMAL', DataTypeCategory.REAL, has_precision=True, is_numeric=True),
            'NUMERIC': DataTypeMapping('NUMERIC', 'NUMERIC', DataTypeCategory.REAL, has_precision=True, is_numeric=True),
            'CHAR': DataTypeMapping('CHAR', 'CHAR', DataTypeCategory.TEXT, has_length=True, is_text=True),
            'VARCHAR': DataTypeMapping('VARCHAR', 'VARCHAR', DataTypeCategory.TEXT, has_length=True, is_text=True),
            'TEXT': DataTypeMapping('TEXT', 'TEXT', DataTypeCategory.TEXT, is_text=True),
            'NCHAR': DataTypeMapping('NCHAR', 'NCHAR', DataTypeCategory.TEXT, has_length=True, is_text=True),
            'NVARCHAR': DataTypeMapping('NVARCHAR', 'NVARCHAR', DataTypeCategory.TEXT, has_length=True, is_text=True),
            'NTEXT': DataTypeMapping('NTEXT', 'NTEXT', DataTypeCategory.TEXT, is_text=True),
            'BINARY': DataTypeMapping('BINARY', 'BINARY', DataTypeCategory.BINARY, is_binary=True),
            'VARBINARY': DataTypeMapping('VARBINARY', 'VARBINARY', DataTypeCategory.BINARY, is_binary=True),
            'IMAGE': DataTypeMapping('IMAGE', 'IMAGE', DataTypeCategory.BINARY, is_binary=True),
            'DATE': DataTypeMapping('DATE', 'DATE', DataTypeCategory.TEMPORAL, is_temporal=True),
            'TIME': DataTypeMapping('TIME', 'TIME', DataTypeCategory.TEMPORAL, is_temporal=True),
            'DATETIME': DataTypeMapping('DATETIME', 'DATETIME', DataTypeCategory.TEMPORAL, is_temporal=True),
            'DATETIME2': DataTypeMapping('DATETIME2', 'DATETIME2', DataTypeCategory.TEMPORAL, is_temporal=True),
            'SMALLDATETIME': DataTypeMapping('SMALLDATETIME', 'SMALLDATETIME', DataTypeCategory.TEMPORAL, is_temporal=True),
            'DATETIMEOFFSET': DataTypeMapping('DATETIMEOFFSET', 'DATETIMEOFFSET', DataTypeCategory.TEMPORAL, is_temporal=True),
            'JSON': DataTypeMapping('JSON', 'JSON', DataTypeCategory.OTHER),
            'XML': DataTypeMapping('XML', 'XML', DataTypeCategory.OTHER),
        }
    
    async def connect(self, **connection_params) -> Any:
        raise NotImplementedError("Use SQLAlchemy engine instead")
    
    async def disconnect(self) -> None:
        pass
    
    async def execute_query(self, query: str, params: Optional[List] = None) -> Any:
        raise NotImplementedError("Use SQLAlchemy engine instead")
    
    async def execute_update(self, query: str, params: Optional[List] = None) -> int:
        raise NotImplementedError("Use SQLAlchemy engine instead")
    
    async def get_databases(self) -> List[str]:
        raise NotImplementedError("Implement with SQLAlchemy engine")
    
    async def get_tables(self, database: str) -> List[str]:
        raise NotImplementedError("Implement with SQLAlchemy inspector")
    
    async def get_views(self, database: str) -> List[str]:
        raise NotImplementedError("Implement with SQLAlchemy inspector")
    
    async def get_procedures(self, database: str) -> List[str]:
        raise NotImplementedError("Implement with SQLAlchemy")
    
    async def get_functions(self, database: str) -> List[str]:
        raise NotImplementedError("Implement with SQLAlchemy")
    
    async def get_triggers(self, database: str, table: Optional[str] = None) -> List[str]:
        raise NotImplementedError("Implement with custom query")
    
    async def get_table_definition(self, database: str, table: str) -> TableDefinition:
        raise NotImplementedError("Implement with SQLAlchemy inspector")
    
    async def get_view_definition(self, database: str, view: str) -> ViewDefinition:
        raise NotImplementedError("Implement with custom query")
    
    async def get_procedure_definition(self, database: str, procedure: str) -> RoutineDefinition:
        raise NotImplementedError("Implement with custom query")
    
    async def get_function_definition(self, database: str, function: str) -> RoutineDefinition:
        raise NotImplementedError("Implement with custom query")
    
    async def get_trigger_definition(self, database: str, trigger: str) -> TriggerDefinition:
        raise NotImplementedError("Implement with custom query")
    
    async def get_row_count(self, database: str, table: str, exact: bool = False) -> int:
        raise NotImplementedError("Implement with custom query")
    
    def get_query_template(self, template_id: QueryTemplateId) -> Optional[str]:
        return self._query_templates.get(template_id)
    
    def format_identifier(self, identifier: str) -> str:
        """Format MSSQL identifier with square brackets"""
        return f"[{identifier}]"
    
    def format_value(self, value: Any, datatype: str) -> str:
        """Format value for MSSQL"""
        if value is None:
            return "NULL"
        if 'INT' in datatype.upper():
            return str(value)
        if 'FLOAT' in datatype.upper() or 'NUMERIC' in datatype.upper() or 'DECIMAL' in datatype.upper():
            return str(value)
        if 'DATE' in datatype.upper() or 'TIME' in datatype.upper():
            return f"'{value}'"
        return f"'{str(value).replace(chr(39), chr(39)*2)}'"


class SQLiteProvider(DatabaseProvider):
    """SQLite provider implementation"""
    
    def _initialize_templates(self) -> None:
        """Initialize SQLite query templates"""
        self._query_templates = {
            QueryTemplateId.DATABASE_TABLE: "SELECT name FROM sqlite_master WHERE type='table'",
        }
    
    def _initialize_data_types(self) -> None:
        """Initialize SQLite data type mappings"""
        self._data_type_map = {
            'INTEGER': DataTypeMapping('INTEGER', 'INTEGER', DataTypeCategory.INTEGER, is_numeric=True),
            'REAL': DataTypeMapping('REAL', 'REAL', DataTypeCategory.REAL, is_numeric=True),
            'TEXT': DataTypeMapping('TEXT', 'TEXT', DataTypeCategory.TEXT, is_text=True),
            'BLOB': DataTypeMapping('BLOB', 'BLOB', DataTypeCategory.BINARY, is_binary=True),
            'NUMERIC': DataTypeMapping('NUMERIC', 'NUMERIC', DataTypeCategory.REAL, is_numeric=True),
            'BOOLEAN': DataTypeMapping('BOOLEAN', 'BOOLEAN', DataTypeCategory.OTHER, is_numeric=True),
        }
    
    async def connect(self, **connection_params) -> Any:
        raise NotImplementedError("Use SQLAlchemy engine instead")
    
    async def disconnect(self) -> None:
        pass
    
    async def execute_query(self, query: str, params: Optional[List] = None) -> Any:
        raise NotImplementedError("Use SQLAlchemy engine instead")
    
    async def execute_update(self, query: str, params: Optional[List] = None) -> int:
        raise NotImplementedError("Use SQLAlchemy engine instead")
    
    async def get_databases(self) -> List[str]:
        raise NotImplementedError("SQLite doesn't have multiple databases")
    
    async def get_tables(self, database: str) -> List[str]:
        raise NotImplementedError("Implement with SQLAlchemy inspector")
    
    async def get_views(self, database: str) -> List[str]:
        raise NotImplementedError("Implement with SQLAlchemy inspector")
    
    async def get_procedures(self, database: str) -> List[str]:
        return []
    
    async def get_functions(self, database: str) -> List[str]:
        return []
    
    async def get_triggers(self, database: str, table: Optional[str] = None) -> List[str]:
        raise NotImplementedError("Implement with custom query")
    
    async def get_table_definition(self, database: str, table: str) -> TableDefinition:
        raise NotImplementedError("Implement with SQLAlchemy inspector")
    
    async def get_view_definition(self, database: str, view: str) -> ViewDefinition:
        raise NotImplementedError("Implement with custom query")
    
    async def get_procedure_definition(self, database: str, procedure: str) -> RoutineDefinition:
        raise NotImplementedError("SQLite doesn't support procedures")
    
    async def get_function_definition(self, database: str, function: str) -> RoutineDefinition:
        raise NotImplementedError("SQLite doesn't support functions")
    
    async def get_trigger_definition(self, database: str, trigger: str) -> TriggerDefinition:
        raise NotImplementedError("Implement with custom query")
    
    async def get_row_count(self, database: str, table: str, exact: bool = False) -> int:
        raise NotImplementedError("Implement with custom query")
    
    def get_query_template(self, template_id: QueryTemplateId) -> Optional[str]:
        return self._query_templates.get(template_id)
    
    def format_identifier(self, identifier: str) -> str:
        """Format SQLite identifier with double quotes"""
        return f'"{identifier.replace(chr(34), chr(34)*2)}"'
    
    def format_value(self, value: Any, datatype: str) -> str:
        """Format value for SQLite"""
        if value is None:
            return "NULL"
        if 'INT' in datatype.upper():
            return str(value)
        if 'REAL' in datatype.upper() or 'NUMERIC' in datatype.upper():
            return str(value)
        if 'DATE' in datatype.upper() or 'TIME' in datatype.upper():
            return f"'{value}'"
        return f"'{str(value).replace(chr(39), chr(39)*2)}'"


def get_provider(database_type: str, server_version: int = 0) -> DatabaseProvider:
    """Factory function to get appropriate database provider"""
    db_type = database_type.lower()
    
    if db_type in ['mysql', 'mariadb']:
        return MySQLProvider(server_version)
    elif db_type == 'postgresql':
        return PostgreSQLProvider(server_version)
    elif db_type == 'mssql':
        return MSSQLProvider(server_version)
    elif db_type == 'sqlite':
        return SQLiteProvider(server_version)
    else:
        raise ValueError(f"Unsupported database type: {database_type}")

