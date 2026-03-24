"""
Setup configuration file for Seneschal Python Edition
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README_PYTHON.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="seneschal-python",
    version="0.1.0",
    author="Seneschal Contributors",
    author_email="support@example.com",
    description="Python port of Seneschal - Multi-database management tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/seneschal-python",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/seneschal-python/issues",
        "Documentation": "https://github.com/yourusername/seneschal-python/wiki",
        "Source Code": "https://github.com/yourusername/seneschal-python",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.8",
    install_requires=[
        "SQLAlchemy>=2.0.0",
        "mysql-connector-python>=8.0.0",
        "psycopg2-binary>=2.9.0",
        "pyodbc>=4.0.0",
        "cryptography>=41.0.0",
        "python-dotenv>=1.0.0",
        "ttkbootstrap>=1.6.0",
        "Pygments>=2.14.0",
        "openpyxl>=3.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "sphinx>=5.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "seneschal-python=seneschal.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: GTK",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: Developers",
        "Intended Audience :: Database Administrators",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: System :: Systems Administration",
    ],
    keywords=[
        "database",
        "management",
        "mysql",
        "postgresql",
        "sql",
        "dba",
        "gui",
        "tkinter",
        "sqlalchemy",
    ],
    include_package_data=True,
    license="GPL-2.0-or-later",
    platforms=[
        "Windows",
        "Linux",
        "macOS",
    ],
    zip_safe=False,
)

