# Seneschal Python Port - Developer Guide

## Architecture Overview

### Layered Architecture

```text
┌─────────────────────────────────────┐
│     UI Layer (Tkinter)              │
│  ├─ MainWindow (main_window.py)     │
│  ├─ Dialogs (dialogs.py)            │
│  └─ Framework (framework.py)        │
├─────────────────────────────────────┤
│     Application Logic               │
│  ├─ Connection Management           │
│  ├─ Query Execution                 │
│  └─ Schema Introspection            │
├─────────────────────────────────────┤
│     Data Access Layer               │
│  ├─ Database Providers (providers.py)│
│  ├─ Connection Manager (connection.py)│
│  └─ Data Models (models.py)         │
├─────────────────────────────────────┤
│     Database (MySQL/PostgreSQL/etc) │
└─────────────────────────────────────┘
```

## Module Descriptions

### Database Layer (`seneschal/db/`)

#### `models.py`

Defines data structures and SQLAlchemy ORM models:

- **Data Classes**:
  - `TableColumn`: Represents a database column
  - `TableKey`: Represents indexes and keys
  - `ForeignKeyConstraint`: Foreign key definitions
  - `TableDefinition`: Complete table schema
  - `ViewDefinition`: View definition
  - `RoutineDefinition`: Procedure/function definition
  - `TriggerDefinition`: Trigger definition

- **ORM Models** (SQLAlchemy):
  - `AuditLog`: Track database changes
  - `ConnectionProfile`: Saved connection profiles
  - `QueryHistory`: User query history

**Key Pattern**: Uses dataclasses for transfer objects, SQLAlchemy ORM for persistence.

#### `providers.py`

Database provider abstraction implementing dialect-specific SQL:

- **QueryTemplateId Enum**: Identifies query types (DATABASE_TABLE, GET_TABLES, etc.)

- **DatabaseProvider** (ABC):
  - Base class for all providers
  - Manages SQL templates and data type mappings
  - Defines interface for schema discovery

- **Concrete Providers**:
  - `MySQLProvider`: MySQL/MariaDB support
  - `PostgreSQLProvider`: PostgreSQL support
  - `MSSQLProvider`: Microsoft SQL Server support
  - `SQLiteProvider`: SQLite support

- **Data Type Mapping**:
  - `DataTypeMapping`: Maps native types to normalized types
  - `DataTypeCategory`: Enum for type categories

**Key Pattern**: Provider pattern for database abstraction, avoiding hard-coded SQL.

#### `connection.py`

Manages database connections and credentials:

- **CredentialManager**:
  - Encrypts/decrypts passwords using Fernet
  - Stores encryption key securely

- **ConnectionManager**:
  - Manages connection profiles (save/load)
  - Creates SQLAlchemy engines with connection pooling
  - Tests connections before use
  - Provides provider instances

**Key Pattern**: Singleton-like connection pool management, encrypted credential storage.

### UI Layer (`seneschal/ui/`)

#### `framework.py`

Base Tkinter components and utilities:

- **UIComponent** (ABC):
  - Base class for all UI components
  - Provides event callback system

- **Components**:
  - `Button`, `Entry`, `Label`, `Frame`: Basic widgets
  - `TreeView`: Hierarchical data (replaces VirtualTrees)
  - `TextEditor`: Multi-line text with syntax highlighting
  - `DataGrid`: Tabular data display (replaces TDBGrid)
  - `Dialog`: Base class for dialogs

- **Container Classes**:
  - `MainWindow`: Application main window (extends ttkbootstrap.Window)
  - `TabManager`: Manages notebook tabs
  - `StatusBar`: Bottom status indicator
  - `MenuBar`: Application menu

- **UITheme**:
  - Configures application appearance

**Key Pattern**: Component-based UI with event callback system, consistent with Tkinter patterns.

#### `dialogs.py`

Dialog windows for user interaction:

- **ConnectionDialog**:
  - Create/edit database connection
  - Test connection functionality
  - Profile persistence

- **LoginDialog**:
  - Select from saved profiles
  - Create new connection

**Key Pattern**: Modal dialogs using Tkinter's Toplevel, async connection testing.

#### `main_window.py`

Main application window and core functionality:

- **SchemaBrowser**:
  - Tree view of databases, tables, views
  - Populates from SQLAlchemy inspector
  - Event handling for tree selection

- **QueryTab**:
  - SQL editor and results grid
  - Query execution with threading
  - Results display and formatting

- **SeneschalApp**:
  - Main application window
  - Menu system
  - Connection management
  - Schema browser integration

**Key Pattern**: Tab-based interface, threaded query execution to avoid UI blocking.

### Entry Point

#### `main.py`

Application bootstrap:

```python
def main():
    app = SeneschalApp(theme='darkly')
    app.run()
```

## Design Patterns Used

### 1. Factory Pattern

```python
# In providers.py
def get_provider(database_type: str) -> DatabaseProvider:
    if db_type == 'mysql':
        return MySQLProvider()
    # ...
```

### 2. Strategy Pattern

```python
# Database providers implement different strategies for SQL generation
class DatabaseProvider(ABC):
    def get_query_template(self, template_id):
        pass  # Each provider implements differently
```

### 3. Connection Pool Pattern

```python
# In connection.py
engine = create_engine(
    connection_string,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10
)
```

### 4. MVC Pattern

```text
Model: SQLAlchemy ORM models
View: Tkinter UI components
Controller: Application logic in main_window.py
```

### 5. Observer Pattern

```python
# UIComponent event system
component.on('event_name', callback)
component.trigger('event_name', args)
```

## Data Flow Examples

### Example 1: Execute Query

```text
User enters SQL in editor
    ↓
Clicks "Execute" button
    ↓
QueryTab._execute_query()
    ↓
SQLAlchemy engine.execute(query)
    ↓
Results fetched from database
    ↓
DataGrid populated with results
    ↓
Results displayed to user
```

### Example 2: Populate Schema Browser

```text
User connects to database
    ↓
ConnectionManager.get_engine(profile)
    ↓
inspect(engine) - SQLAlchemy inspector
    ↓
inspector.get_schema_names()
    ↓
For each schema: inspector.get_table_names()
    ↓
TreeView populated with hierarchy
    ↓
Schema structure displayed to user
```

### Example 3: Save Connection Profile

```text
User fills connection dialog
    ↓
ConnectionDialog.show()
    ↓
ConnectionManager.add_profile(conn_info)
    ↓
CredentialManager.encrypt(password)
    ↓
profiles.json updated with encrypted data
    ↓
Connection saved locally
```

## Threading Model

### Main Thread

- Handles all Tkinter UI updates
- Manages event loop

### Background Threads

- Query execution (via ThreadPoolExecutor)
- Schema discovery
- Connection testing

```python
# Example: Execute query asynchronously
loop = asyncio.new_event_loop()
threading.Thread(
    target=lambda: loop.run_until_complete(coro),
    daemon=True
).start()
```

## Error Handling Strategy

### Database Errors

```python
try:
    result = conn.execute(text(query))
except SQLAlchemyError as e:
    messagebox.showerror("Query Error", str(e))
except Exception as e:
    messagebox.showerror("Error", str(e))
```

### Connection Errors

```python
try:
    engine = create_engine(connection_string)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
except ConnectionError as e:
    messagebox.showerror("Connection Error", str(e))
```

## Configuration Management

### Profile Storage

```json
{
    "My Connection": {
        "db_type": "mysql",
        "host": "localhost",
        "port": 3306,
        "database": "testdb",
        "username": "root",
        "password_encrypted": "gAAAAAB...",
        "charset": "utf8mb4",
        "ssl_enabled": false
    }
}
```

### Encryption

- Uses Fernet (symmetric encryption)
- Key stored in `~/.seneschal/credentials.key`
- File permissions: 0o600 (read/write by owner only)

## Extension Points

### Adding a New Database Provider

1. Create provider class in `providers.py`:

```python
class CustomDBProvider(DatabaseProvider):
    def _initialize_templates(self):
        self._query_templates = {
            QueryTemplateId.DATABASE_TABLE: "CUSTOM SQL"
        }
    
    def _initialize_data_types(self):
        self._data_type_map = {
            'CUSTOM_TYPE': DataTypeMapping(...)
        }
    
    # Implement abstract methods
```

1. Register in factory:

```python
def get_provider(database_type: str):
    if database_type == 'customdb':
        return CustomDBProvider()
```

### Adding a New UI Component

1. Extend UIComponent:

```python
class CustomComponent(UIComponent):
    def build(self) -> tk.Widget:
        self.widget = tk.CustomWidget(self.parent)
        return self.widget
```

1. Use in main window:

```python
component = CustomComponent(parent)
widget = component.build()
widget.pack()
```

## Testing Strategy

### Unit Tests

- Test database providers independently
- Test connection manager
- Test data model serialization

### Integration Tests

- Test actual database connections
- Test query execution
- Test schema introspection

### UI Tests

- Test dialog interactions
- Test component rendering
- Test event callbacks

## Performance Considerations

### Connection Pooling

- QueuePool with max_overflow for connection efficiency
- Pool recycled every 1 hour
- Connections tested before use

### Query Optimization

- Use LIMIT for large result sets
- Implement pagination for grids
- Cache schema information

### UI Responsiveness

- Background threads for long operations
- Async/await for non-blocking operations
- Progress indicators for operations

## Security Practices

### Credential Management

- Passwords encrypted with Fernet
- Encryption key stored securely
- No passwords in logs or configuration

### SQL Injection Prevention

- Use parameterized queries
- SQLAlchemy handles escaping

### Data Access

- Connection pooling reduces exposure
- Each connection is isolated

## Debugging Tips

### Enable SQLAlchemy Logging

```python
engine = create_engine(connection_string, echo=True)
```

### Enable Application Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Print Stack Traces

```python
import traceback
try:
    # code
except Exception as e:
    traceback.print_exc()
```

## Build and Deployment

### Development Installation

```bash
pip install -e .
```

### Production Build

```bash
python setup.py sdist bdist_wheel
```

### Running Tests

```bash
pytest tests/
```

### Creating Distribution

```bash
pip install build
python -m build
```

---

### For questions or contributions, refer to the project README
