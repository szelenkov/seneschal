# Quick Start Guide - Seneschal Python Edition

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or navigate to the project**

```bash
cd ~\seneschal
```

2. **Create virtual environment (recommended)**

```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Install the application**

```bash
pip install -e .
```

## Running the Application

### Method 1: Direct Python

```bash
python -m seneschal.main
```

### Method 2: Using entry point

```bash
seneschal-python
```

## First Time Setup

1. **Launch the application**
   - The login dialog will appear
   - Click "New Connection" to create your first database connection

2. **Create a Connection**
   - Enter a connection name (e.g., "Production MySQL")
   - Select database type (MySQL, PostgreSQL, MSSQL, SQLite)
   - Enter connection details (host, port, username, password)
   - Click "Test Connection" to verify
   - Click "OK" to save

3. **Connect to Database**
   - Select your connection from the list
   - Click "Connect"
   - The schema browser will populate with databases and tables

## Basic Usage

### Query Execution

1. **Write a query**
   - Type SQL in the query editor
   - Example: `SELECT * FROM users WHERE age > 30;`

2. **Execute query**
   - Click the "Execute" button (or Ctrl+Enter)
   - Results appear in the grid below

3. **View results**
   - Each row can be clicked and selected
   - Columns are shown as headers
   - Scroll to see more data

### Schema Browser

- **Left sidebar** shows database hierarchy
- **Double-click** database to expand
- **View tables, views, and other objects**
- **Right-click** for context menu (future enhancement)

### Connection Management

- **File → New Connection**: Create new connection
- **File → Open Connection**: Switch connections
- **File → Manage Connections**: View/edit saved connections

## Supported Databases

### Fully Supported

- MySQL 5.7+
- MariaDB 10.1+
- PostgreSQL 9.6+
- SQLite 3+

### Planned Support

- Microsoft SQL Server 2012+
- Firebird 2.5+

## Keyboard Shortcuts

| Shortcut   | Action             |
|------------|--------------------|
| Ctrl+Enter | Execute query      |
| Ctrl+N     | New query tab      |
| Ctrl+W     | Close query tab    |
| Ctrl+E     | Export results     |
| Ctrl+H     | Show query history |

## Configuration Files

### Saved Connections

```tetx
~/.seneschal/profiles.json
```

Contains encrypted connection profiles

### Credentials

```text
~/.seneschal/credentials.key
```

Encryption key for password storage

### Logs

```text
~/.seneschal/logs/
```

Application logs for debugging

## Troubleshooting

### Connection Failed

1. Check database server is running
2. Verify host and port settings
3. Confirm username and password
4. Check firewall settings
5. Review error message in dialog

### Query Execution Error

1. Check SQL syntax
2. Verify table/column names exist
3. Check user has required permissions
4. Review error message in results area

### Application Won't Start

1. Ensure Python 3.8+ installed
2. Check dependencies installed: `pip install -r requirements.txt`
3. Check logs in `~/.seneschal/logs/`
4. Try reinstalling: `pip install --force-reinstall -e .`

## Performance Tips

### Large Datasets

- Use LIMIT clause: `SELECT * FROM huge_table LIMIT 1000;`
- Add WHERE conditions to filter data
- Avoid SELECT * on wide tables

### Slow Queries

- Check table indexes
- Use EXPLAIN to analyze query plan
- Consider query optimization

## Development Notes

### Adding Database Support

1. Create provider class in `db/providers.py`
2. Implement required abstract methods
3. Add data type mappings
4. Update documentation

### Custom UI Components

1. Extend `UIComponent` in `ui/framework.py`
2. Implement `build()` method
3. Add event callbacks as needed

### Database Access Pattern

```python
# Example: Execute query
from seneschal.db.connection import ConnectionManager

conn_mgr = ConnectionManager()
engine = conn_mgr.get_engine("profile_name")

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users"))
    for row in result:
        print(row)
```

## Roadmap

### v0.2.0 (Current Development)

- SQL syntax highlighting
- Query history
- Export to CSV/JSON
- Table editor

### v0.3.0

- Advanced data grid features
- Find & replace
- Database backup/restore

### v0.4.0

- Stored procedures editor
- Trigger management
- User management

### v1.0.0

- Feature parity with Seneschal
- Full database support
- Advanced tools

## Getting Help

### Documentation

- See `CONVERSION_PROGRESS.md` for architecture details
- Check `README.md` for project overview

### Issues

- Report bugs in GitHub Issues
- Include error messages and steps to reproduce

### Contributing

- Submit pull requests with new features
- Follow PEP 8 code style
- Include unit tests for new code

## License

Seneschal Python Edition is licensed under GPL-2.0-or-later.

---

**Version**: 0.1.0  
**Last Updated**: 2026-03-22  
**Status**: Alpha (Foundation Phase Complete)
