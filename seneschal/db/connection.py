"""
Database connection manager.
Handles connection profiles, credential management, and connection pooling.
"""

import os
import json
from typing import Optional, Dict, List
from pathlib import Path
from dataclasses import dataclass, asdict
import asyncio
from threading import Lock

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from cryptography.fernet import Fernet
import dotenv

from .models import ConnectionProfile
from .providers import get_provider, DatabaseProvider


@dataclass
class ConnectionInfo:
    """Connection information"""
    name: str
    db_type: str
    host: str
    port: int
    database: str
    username: str
    password: str
    charset: Optional[str] = None
    ssl_enabled: bool = False
    ssh_enabled: bool = False


class CredentialManager:
    """Manages encrypted credential storage"""
    
    def __init__(self, key_file: Optional[str] = None):
        """Initialize credential manager"""
        if key_file is None:
            key_file = os.path.expanduser("~/.seneschal/credentials.key")
        
        self.key_file = Path(key_file)
        self.key_file.parent.mkdir(parents=True, exist_ok=True)
        self._cipher = self._load_or_create_key()
    
    def _load_or_create_key(self) -> Fernet:
        """Load or create encryption key"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # Restrict file permissions
            os.chmod(self.key_file, 0o600)
        
        return Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt password"""
        return self._cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt password"""
        return self._cipher.decrypt(ciphertext.encode()).decode()


class ConnectionManager:
    """Manages database connections"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize connection manager"""
        if config_dir is None:
            config_dir = os.path.expanduser("~/.seneschal")
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.credential_mgr = CredentialManager(str(self.config_dir / "credentials.key"))
        self.connections: Dict[str, Engine] = {}
        self.providers: Dict[str, DatabaseProvider] = {}
        self.profiles: Dict[str, ConnectionInfo] = {}
        self._lock = Lock()
        
        self._load_profiles()
    
    def _load_profiles(self) -> None:
        """Load saved connection profiles from config"""
        profiles_file = self.config_dir / "profiles.json"
        
        if profiles_file.exists():
            with open(profiles_file, 'r') as f:
                profiles_data = json.load(f)
                for profile_name, profile_info in profiles_data.items():
                    try:
                        conn_info = ConnectionInfo(
                            name=profile_name,
                            db_type=profile_info['db_type'],
                            host=profile_info.get('host', 'localhost'),
                            port=profile_info.get('port', 3306),
                            database=profile_info.get('database', ''),
                            username=profile_info.get('username', ''),
                            password=self.credential_mgr.decrypt(profile_info.get('password_encrypted', '')) if profile_info.get('password_encrypted') else '',
                            charset=profile_info.get('charset'),
                            ssl_enabled=profile_info.get('ssl_enabled', False),
                            ssh_enabled=profile_info.get('ssh_enabled', False)
                        )
                        self.profiles[profile_name] = conn_info
                    except Exception as e:
                        print(f"Failed to load profile {profile_name}: {e}")
    
    def _save_profiles(self) -> None:
        """Save connection profiles to config"""
        profiles_file = self.config_dir / "profiles.json"
        
        profiles_data = {}
        for profile_name, conn_info in self.profiles.items():
            profiles_data[profile_name] = {
                'db_type': conn_info.db_type,
                'host': conn_info.host,
                'port': conn_info.port,
                'database': conn_info.database,
                'username': conn_info.username,
                'password_encrypted': self.credential_mgr.encrypt(conn_info.password),
                'charset': conn_info.charset,
                'ssl_enabled': conn_info.ssl_enabled,
                'ssh_enabled': conn_info.ssh_enabled
            }
        
        with open(profiles_file, 'w') as f:
            json.dump(profiles_data, f, indent=2)
    
    def add_profile(self, conn_info: ConnectionInfo) -> None:
        """Add connection profile"""
        with self._lock:
            self.profiles[conn_info.name] = conn_info
            self._save_profiles()
    
    def delete_profile(self, name: str) -> None:
        """Delete connection profile"""
        with self._lock:
            if name in self.profiles:
                del self.profiles[name]
            if name in self.connections:
                self.connections[name].dispose()
                del self.connections[name]
            if name in self.providers:
                del self.providers[name]
            self._save_profiles()
    
    def get_profile(self, name: str) -> Optional[ConnectionInfo]:
        """Get connection profile by name"""
        return self.profiles.get(name)
    
    def list_profiles(self) -> List[str]:
        """List all saved profiles"""
        return list(self.profiles.keys())
    
    def _build_connection_string(self, conn_info: ConnectionInfo) -> str:
        """Build SQLAlchemy connection string"""
        db_type = conn_info.db_type.lower()
        
        if db_type in ['mysql', 'mariadb']:
            driver = 'mysql+mysqlconnector' if 'mysql-connector' in str(__import__('pkg_resources').working_set) else 'mysql+pymysql'
            charset = conn_info.charset or 'utf8mb4'
            return (f"{driver}://{conn_info.username}:{conn_info.password}"
                   f"@{conn_info.host}:{conn_info.port}"
                   f"/?charset={charset}")
        
        elif db_type == 'postgresql':
            return (f"postgresql+psycopg2://{conn_info.username}:{conn_info.password}"
                   f"@{conn_info.host}:{conn_info.port}/{conn_info.database}")
        
        elif db_type == 'mssql':
            driver = 'mssql+pyodbc'
            return (f"{driver}://{conn_info.username}:{conn_info.password}"
                   f"@{conn_info.host}:{conn_info.port}/{conn_info.database}"
                   f"?driver=ODBC+Driver+17+for+SQL+Server")
        
        elif db_type == 'sqlite':
            # For SQLite, host is the file path
            return f"sqlite:///{conn_info.host}"
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def get_engine(self, profile_name: str, echo: bool = False) -> Engine:
        """Get SQLAlchemy engine for profile"""
        with self._lock:
            if profile_name in self.connections:
                return self.connections[profile_name]
            
            conn_info = self.get_profile(profile_name)
            if not conn_info:
                raise ValueError(f"Profile not found: {profile_name}")
            
            connection_string = self._build_connection_string(conn_info)
            
            # Create engine with connection pooling
            engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_recycle=3600,
                echo=echo
            )
            
            # Test connection
            try:
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
            except Exception as e:
                raise ConnectionError(f"Failed to connect to {profile_name}: {e}")
            
            self.connections[profile_name] = engine
            return engine
    
    def get_provider(self, profile_name: str) -> DatabaseProvider:
        """Get database provider for profile"""
        if profile_name in self.providers:
            return self.providers[profile_name]
        
        conn_info = self.get_profile(profile_name)
        if not conn_info:
            raise ValueError(f"Profile not found: {profile_name}")
        
        provider = get_provider(conn_info.db_type)
        self.providers[profile_name] = provider
        return provider
    
    async def test_connection(self, conn_info: ConnectionInfo) -> tuple[bool, str]:
        """Test database connection"""
        try:
            # Temporarily create engine
            connection_string = self._build_connection_string(conn_info)
            engine = create_engine(connection_string, poolclass=QueuePool)
            
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            engine.dispose()
            return True, "Connection successful"
        
        except Exception as e:
            return False, str(e)
    
    def close_connection(self, profile_name: str) -> None:
        """Close database connection"""
        with self._lock:
            if profile_name in self.connections:
                self.connections[profile_name].dispose()
                del self.connections[profile_name]
    
    def close_all(self) -> None:
        """Close all connections"""
        with self._lock:
            for engine in self.connections.values():
                engine.dispose()
            self.connections.clear()
            self.providers.clear()

