# Seneschal Python Version

A Python port of the popular Seneschal database management tool, providing a modern interface for managing multiple database systems including MySQL, PostgreSQL, SQLite, and MS SQL Server.

## Features

- Multi-database system support (MySQL, PostgreSQL, SQLite, MS SQL Server)
- Modern PyQt6-based user interface
- Database connection management
- SQL query execution
- Database structure browsing
- Table data viewing and editing (coming soon)
- Export/Import capabilities (coming soon)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/seneschal-python.git
cd seneschal-python
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python -m seneschal.main
```

## Development Setup

This project uses:
- Python 3.8+
- PyQt6 for the GUI
- SQLAlchemy for database operations
- Various database drivers (mysql-connector-python, psycopg2, etc.)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the GPL License - see the LICENSE file for details.

## Acknowledgments

- Original Seneschal project and its contributors
- PyQt and SQLAlchemy communities
