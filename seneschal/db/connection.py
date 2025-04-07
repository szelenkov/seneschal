from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

from sqlalchemy import create_engine, Engine, text
from sqlalchemy.exc import SQLAlchemyError


class DatabaseConnection(ABC):
    def __init__(self):
        self.engine: Optional[Engine] = None
        self.connected: bool = False
        self.current_database: Optional[str] = None
        
    @abstractmethod
    def connect(self, params: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        pass
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> Any:
        if not self.connected or not self.engine:
            raise ConnectionError("Not connected to database")
        try:
            with self.engine.connect() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                return result
        except SQLAlchemyError as e:
            raise Exception(f"Query execution failed: {str(e)}")
            
    def get_databases(self) -> List[str]:
        """Get list of databases"""
        if not self.connected or not self.engine:
            return []
        try:
            result = self.execute_query("SHOW DATABASES")
            return [row[0] for row in result]
        except Exception:
            return []
            
    def get_tables(self, database: str) -> List[str]:
        """Get list of tables in the specified database"""
        if not self.connected or not self.engine:
            return []
        try:
            self.execute_query(f"USE {database}")
            result = self.execute_query("SHOW TABLES")
            return [row[0] for row in result]
        except Exception:
            return []

class MySQLConnection(DatabaseConnection):
    def connect(self, params: Dict[str, Any]) -> bool:
        try:
            connection_string = (
                f"mysql+mysqlconnector://{params['user']}:{params['password']}"
                f"@{params['host']}:{params['port']}/{params.get('database', '')}"
            )
            self.engine = create_engine(connection_string)
            self.engine.connect()  # Test connection
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            raise Exception(f"MySQL connection failed: {str(e)}")
    
    def disconnect(self) -> bool:
        if self.engine:
            self.engine.dispose()
            self.connected = False
        return True

class PostgreSQLConnection(DatabaseConnection):
    def connect(self, params: Dict[str, Any]) -> bool:
        try:
            connection_string = (
                f"postgresql+psycopg2://{params['user']}:{params['password']}"
                f"@{params['host']}:{params['port']}/{params.get('database', '')}"
            )
            self.engine = create_engine(connection_string)
            self.engine.connect()  # Test connection
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            raise Exception(f"PostgreSQL connection failed: {str(e)}")
    
    def disconnect(self) -> bool:
        if self.engine:
            self.engine.dispose()
            self.connected = False
        return True

class SQLiteConnection(DatabaseConnection):
    def connect(self, params: Dict[str, Any]) -> bool:
        try:
            connection_string = f"sqlite:///{params['database']}"
            self.engine = create_engine(connection_string)
            self.engine.connect()  # Test connection
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            raise Exception(f"SQLite connection failed: {str(e)}")
    
    def disconnect(self) -> bool:
        if self.engine:
            self.engine.dispose()
            self.connected = False
        return True
