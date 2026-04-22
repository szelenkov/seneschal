# Seneschal Python Edition

A Python port of the popular [Seneschal](.) database management tool, a cross-platform Python application using Tkinter for the UI and SQLAlchemy for database access.

## 🎯 Project Goal

- ✅ Support for multiple database types
- ✅ Cross-platform compatibility (Windows, Linux, macOS)

## 📋 Status

**Current Phase**: Foundation (v0.1.0 - Alpha)

### Completed ✅

- Core database abstraction layer with provider pattern
- SQLAlchemy ORM integration
- Tkinter UI framework
- Connection management with encrypted credentials
- Login and connection dialogs
- Query editor with results grid
- Schema browser with database hierarchy
- Multi-database support (MySQL, PostgreSQL, MSSQL, SQLite)

### In Progress 🔄

- SQL syntax highlighting
- Query history
- Data export (CSV, JSON, Excel)
- Table editor UI

### Planned 📅

- Advanced data grid features (sorting, filtering, editing)
- Stored procedures/functions/triggers editor
- Database maintenance tools
- User and permission management
- Advanced search and replace

## 🏗️ Architecture

### Layered Design

```text
┌──────────────────────────────────┐
│   UI Layer (Tkinter)             │
│  ├─ Main Window                  │
│  ├─ Dialogs                      │
│  └─ UI Components                │
├──────────────────────────────────┤
│   Business Logic                 │
│  ├─ Connection Management        │
│  ├─ Query Execution              │
│  └─ Schema Discovery             │
├──────────────────────────────────┤
│   Data Access (SQLAlchemy)       │
│  ├─ Database Providers           │
│  ├─ ORM Models                   │
│  └─ Connection Pool              │
├──────────────────────────────────┤
│   Database Servers               │
└──────────────────────────────────┘
```

### Key Design Patterns

- **Factory Pattern**: Database provider selection
- **Strategy Pattern**: Database-specific SQL generation
- **MVC Pattern**: Separation of concerns
- **Connection Pool Pattern**: Efficient resource management
- **Observer Pattern**: Event system for UI

## 📦 Installation

### Requirements

- Python 3.8 or higher
- pip package manager

### Setup

1. **Navigate to project**

```bash
cd ~\seneschal
```

1. **Create virtual environment**

```bash
python -m venv venv
venv\Scripts\activate
```

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

1. **Install application**

```bash
pip install -e .
```

## 🚀 Usage

### Start Application

```bash
python -m seneschal.main
```

Or using entry point:

```bash
seneschal-python
```

### First Connection

1. Click "New Connection" in login dialog
2. Fill connection details
3. Click "Test Connection"
4. Click "OK" to save and connect

### Execute Query

1. Type SQL in query editor
2. Click "Execute" button or press Ctrl+Enter
3. View results in grid below

## 📚 Documentation

- **[QUICKSTART.md](./QUICKSTART.md)** - Quick start guide for end users
- **[DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)** - Detailed architecture and development guide

## 🗄️ Database Support

### Fully Supported

- ✅ MySQL 5.7+
- ✅ MariaDB 10.1+
- ✅ PostgreSQL 9.6+
- ✅ SQLite 3+

### Planned Support

- 🔄 Microsoft SQL Server 2012+
- 🔄 Firebird 2.5+

## 🛠️ Tech Stack

### Frontend

- **Tkinter**: GUI framework
- **ttkbootstrap**: Enhanced theming

### Backend

- **SQLAlchemy 2.0+**: ORM and database abstraction
- **SQLAlchemy Core**: Direct SQL execution

### Database Drivers

- **mysql-connector-python**: MySQL support
- **psycopg2**: PostgreSQL support
- **pyodbc**: MSSQL support

### Utilities

- **cryptography**: Password encryption
- **Pygments**: SQL syntax highlighting
- **openpyxl**: Excel export

## 📁 Project Structure

```text
seneschal/
├── main.py                      # Application entry point
├── __init__.py                  # Package initialization
│
├── db/                          # Database layer
│   ├── __init__.py
│   ├── models.py               # Data models and ORM
│   ├── providers.py            # Database provider abstraction
│   └── connection.py           # Connection management
│
├── ui/                         # UI layer
│   ├── __init__.py
│   ├── framework.py            # Base UI components
│   ├── dialogs.py              # Dialog windows
│   └── main_window.py          # Main application
│
├── tools/                      # Utility modules (future)
│   └── __init__.py
│
└── utils/                      # Helper functions (future)
    └── __init__.py

tests/
├── __init__.py
└── test_basic.py              # Unit tests

docs/
├── QUICKSTART.md              # Quick start guide
├── DEVELOPER_GUIDE.md         # Development documentation
├── CONVERSION_PROGRESS.md     # Migration progress tracker
└── README.md                  # This file

Configuration Files
├── pyproject.toml             # Project metadata
├── requirements.txt           # Python dependencies
└── settings.ini               # Application settings
```

## 🔐 Security

### Credential Management

- Passwords encrypted with Fernet (symmetric encryption)
- Encryption key stored securely with restricted permissions
- Profiles saved as JSON with encrypted passwords

### SQL Safety

- Uses parameterized queries via SQLAlchemy
- Protection against SQL injection
- Connection pooling with secure session management

## 🧪 Testing

### Run Unit Tests

```bash
python -m pytest tests/
```

### Run Specific Test

```bash
python -m pytest tests/test_basic.py::TestDataModels
```

### Test Coverage

```bash
python -m pytest --cov=seneschal tests/
```

## 🎨 UI Features

### Query Editor

- Multi-line SQL editor
- Syntax highlighting support
- Query execution with results
- Multiple query tabs

### Schema Browser

- Database hierarchy view
- Table/view browser
- Object properties display
- Context menu (future)

### Data Grid

- Sortable columns (future)
- Filtering (future)
- In-place editing (future)
- Export to multiple formats (future)

### Dialogs

- Connection creation/editing
- Login selection
- Query history (future)
- Preferences (future)

## 🔄 Data Flow Examples

### Example 1: User Executes Query

```text
User writes SQL in editor
  ↓
Clicks "Execute" button
  ↓
QueryTab._execute_query() method called
  ↓
Gets SQLAlchemy engine via ConnectionManager
  ↓
engine.execute(text(query))
  ↓
Results fetched from database
  ↓
DataGrid populated with columns and rows
  ↓
Results displayed to user with row count
```

### Example 2: User Creates Connection

```text
User clicks "New Connection"
  ↓
ConnectionDialog shown
  ↓
User fills connection details
  ↓
Clicks "Test Connection"
  ↓
ConnectionManager.test_connection()
  ↓
SQLAlchemy engine created temporarily
  ↓
Test query executed
  ↓
Result shown to user
  ↓
User clicks OK
  ↓
CredentialManager encrypts password
  ↓
ConnectionManager saves profile
  ↓
Profile persisted to profiles.json
```

### Example 3: Schema Discovery

```text
User connects to database
  ↓
ConnectionManager creates engine
  ↓
SQLAlchemy Inspector created
  ↓
get_schema_names() called
  ↓
For each schema:
  get_table_names() called
  get_view_names() called
  ↓
TreeView populated with hierarchy
  ↓
User sees databases and tables
```

## 🚦 Keyboard Shortcuts

| Shortcut   | Action             |
|------------|--------------------|
| Ctrl+Enter | Execute query      |
| Ctrl+N     | New query tab      |
| Ctrl+W     | Close query tab    |
| Ctrl+E     | Export results     |
| Ctrl+H     | Show query history |

## 📝 Migration Notes

### Key Differences

1. **Threading**: Uses Python threading
2. **UI Framework**: Tkinter instead of VCL/FireMonkey
3. **Database Access**: SQLAlchemy instead of FireDAC
4. **Configuration**: JSON files instead of INI/Registry
5. **Error Handling**: Exception objects instead of error codes

## 🐛 Troubleshooting

### Connection Failed

- Verify database server is running
- Check host and port settings
- Confirm username/password
- Review error message in dialog

### Query Errors

- Check SQL syntax
- Verify table/column names
- Check user permissions
- See error message in results area

### Application Won't Start

- Ensure Python 3.8+ installed
- Install dependencies: `pip install -r requirements.txt`
- Check ~/.seneschal/logs/ for error details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add unit tests for new features
- Update documentation
- Keep commits atomic and descriptive

## 📋 Roadmap

### v0.2.0

- SQL syntax highlighting
- Query history tracking
- CSV/JSON export
- Basic table editor

### v0.3.0

- Advanced data grid features
- Find and replace
- Database backup/restore
- User management

### v0.4.0

- Stored procedures editor
- Trigger management
- Advanced maintenance tools

### v1.0.0

- Feature parity with Seneschal
- Full multi-database support
- Production ready

## 📄 License

This project is licensed under **GPL-2.0-or-later**.

## 👏 Credits

**Python Port**: Community effort as part of application modernization

## 💬 Getting Help

### Documentation

- See [QUICKSTART.md](./QUICKSTART.md) for user guide
- See [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md) for technical details

### Support

- Check existing GitHub Issues
- Create new Issue with detailed description
- Include error messages and reproduction steps

## 🙌 Acknowledgments

- Python community for excellent libraries (SQLAlchemy, Tkinter, etc.)
- Contributors and testers

---

**Version**: 0.1.0 (Alpha)  
**Last Updated**: 2026-03-22  
**Status**: Foundation Phase Complete - Ready for Phase 2 Development

For detailed development information, see [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)
