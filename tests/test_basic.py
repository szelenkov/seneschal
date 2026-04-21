"""
Unit tests for Seneschal Python port
"""

import unittest
import tempfile
import os
from pathlib import Path

from seneschal.db.models import TableColumn, TableKey, TableDefinition
from seneschal.db.providers import MySQLProvider, PostgreSQLProvider, get_provider
from seneschal.db.connection import CredentialManager, ConnectionInfo


class TestDataModels(unittest.TestCase):
    """Test data model classes"""
    
    def test_table_column_creation(self):
        """Test creating a table column"""
        col = TableColumn(
            name="user_id",
            data_type="INT",
            allow_null=False
        )
        
        self.assertEqual(col.name, "user_id")
        self.assertEqual(col.data_type, "INT")
        self.assertFalse(col.allow_null)
    
    def test_table_key_creation(self):
        """Test creating a table key"""
        key = TableKey(
            name="PK_users",
            key_type="PRIMARY",
            columns=["user_id"]
        )
        
        self.assertEqual(key.name, "PK_users")
        self.assertTrue(key.is_primary)
    
    def test_table_definition_creation(self):
        """Test creating a table definition"""
        col = TableColumn(name="id", data_type="INT")
        key = TableKey(name="PK_id", key_type="PRIMARY", columns=["id"])
        
        table = TableDefinition(
            name="users",
            schema="public",
            columns=[col],
            keys=[key]
        )
        
        self.assertEqual(table.name, "users")
        self.assertEqual(len(table.columns), 1)
        self.assertEqual(len(table.keys), 1)


class TestDatabaseProviders(unittest.TestCase):
    """Test database provider implementations"""
    
    def test_mysql_provider_creation(self):
        """Test MySQL provider instantiation"""
        provider = MySQLProvider()
        
        self.assertIsNotNone(provider)
        self.assertTrue(provider.supports_query_template(__import__('seneschal.db.providers', fromlist=['QueryTemplateId']).QueryTemplateId.DATABASE_TABLE))
    
    def test_postgresql_provider_creation(self):
        """Test PostgreSQL provider instantiation"""
        provider = PostgreSQLProvider()
        
        self.assertIsNotNone(provider)
    
    def test_provider_factory(self):
        """Test provider factory function"""
        mysql = get_provider("mysql")
        postgres = get_provider("postgresql")
        
        self.assertIsNotNone(mysql)
        self.assertIsNotNone(postgres)
        
        # Test unsupported type
        with self.assertRaises(ValueError):
            get_provider("unsupported_db")
    
    def test_mysql_identifier_formatting(self):
        """Test MySQL identifier formatting"""
        provider = MySQLProvider()
        
        result = provider.format_identifier("users")
        self.assertEqual(result, "`users`")
    
    def test_mysql_value_formatting(self):
        """Test MySQL value formatting"""
        provider = MySQLProvider()
        
        # Integer
        result = provider.format_value(42, "INT")
        self.assertEqual(result, "42")
        
        # String
        result = provider.format_value("test", "VARCHAR")
        self.assertEqual(result, "'test'")
        
        # NULL
        result = provider.format_value(None, "VARCHAR")
        self.assertEqual(result, "NULL")
    
    def test_postgresql_identifier_formatting(self):
        """Test PostgreSQL identifier formatting"""
        provider = PostgreSQLProvider()
        
        result = provider.format_identifier("users")
        self.assertEqual(result, '"users"')
    
    def test_mssql_identifier_formatting(self):
        """Test MSSQL identifier formatting"""
        from seneschal.db.providers import MSSQLProvider
        provider = MSSQLProvider()
        
        result = provider.format_identifier("users")
        self.assertEqual(result, "[users]")


class TestCredentialManager(unittest.TestCase):
    """Test credential encryption"""
    
    def setUp(self):
        """Create temporary key file"""
        self.temp_dir = tempfile.mkdtemp()
        self.key_file = os.path.join(self.temp_dir, "test.key")
    
    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.key_file):
            os.remove(self.key_file)
        os.rmdir(self.temp_dir)
    
    def test_encrypt_decrypt(self):
        """Test password encryption and decryption"""
        mgr = CredentialManager(self.key_file)
        
        password = "SecurePassword123!"
        encrypted = mgr.encrypt(password)
        decrypted = mgr.decrypt(encrypted)
        
        self.assertEqual(password, decrypted)
        self.assertNotEqual(password, encrypted)
    
    def test_key_persistence(self):
        """Test that key is persisted"""
        mgr1 = CredentialManager(self.key_file)
        password = "Test123"
        encrypted = mgr1.encrypt(password)
        
        # Create new manager with same key
        mgr2 = CredentialManager(self.key_file)
        decrypted = mgr2.decrypt(encrypted)
        
        self.assertEqual(password, decrypted)


class TestConnectionInfo(unittest.TestCase):
    """Test connection information"""
    
    def test_connection_info_creation(self):
        """Test creating connection info"""
        conn_info = ConnectionInfo(
            name="test_connection",
            db_type="mysql",
            host="localhost",
            port=3306,
            database="testdb",
            username="root",
            password="password"
        )
        
        self.assertEqual(conn_info.name, "test_connection")
        self.assertEqual(conn_info.host, "localhost")
        self.assertEqual(conn_info.port, 3306)


class TestUIComponents(unittest.TestCase):
    """Test UI framework components"""
    
    def test_ui_component_import(self):
        """Test importing UI components"""
        from seneschal.ui.framework import (
            Button, Entry, Label, Frame,
            TreeView, TextEditor, DataGrid
        )
        
        self.assertIsNotNone(Button)
        self.assertIsNotNone(Entry)
        self.assertIsNotNone(Label)
        self.assertIsNotNone(Frame)
        self.assertIsNotNone(TreeView)
        self.assertIsNotNone(TextEditor)
        self.assertIsNotNone(DataGrid)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_module_imports(self):
        """Test all major modules can be imported"""
        # DB module
        from seneschal.db import models, providers, connection
        self.assertIsNotNone(models)
        self.assertIsNotNone(providers)
        self.assertIsNotNone(connection)
        
        # UI module
        from seneschal.ui import framework, dialogs, main_window
        self.assertIsNotNone(framework)
        self.assertIsNotNone(dialogs)
        self.assertIsNotNone(main_window)
    
    def test_connection_manager_creation(self):
        """Test creating connection manager"""
        temp_dir = tempfile.mkdtemp()
        try:
            from seneschal.db.connection import ConnectionManager
            mgr = ConnectionManager(temp_dir)
            
            self.assertIsNotNone(mgr)
            self.assertEqual(len(mgr.list_profiles()), 0)
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_profile_persistence(self):
        """Test saving and loading profiles"""
        temp_dir = tempfile.mkdtemp()
        try:
            from seneschal.db.connection import ConnectionManager, ConnectionInfo
            
            mgr = ConnectionManager(temp_dir)
            
            # Add profile
            conn_info = ConnectionInfo(
                name="test_profile",
                db_type="mysql",
                host="localhost",
                port=3306,
                database="test",
                username="root",
                password="pass123"
            )
            mgr.add_profile(conn_info)
            
            # Create new manager and check profile persists
            mgr2 = ConnectionManager(temp_dir)
            profiles = mgr2.list_profiles()
            
            self.assertIn("test_profile", profiles)
            self.assertEqual(len(profiles), 1)
            
            # Check profile data
            loaded = mgr2.get_profile("test_profile")
            self.assertEqual(loaded.name, "test_profile")
            self.assertEqual(loaded.password, "pass123")
        
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()

