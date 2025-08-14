# Database Setup and Data Loading

This directory contains all the database-related scripts and utilities for the Wuzzuf Job Market Analysis project.

## 🔐 Security Notice

**IMPORTANT**: Database credentials are handled securely and are NOT committed to Git. Follow the setup instructions below to configure your database connection safely.

## 📁 Files Overview

### Core Files
- `schema.sql` - PostgreSQL database schema with tables, indexes, and views
- `database_setup.py` - Database connection utilities and management
- `data_insertion.py` - Complete data insertion pipeline
- `setup_config.py` - Secure configuration setup script

### Documentation
- `schema_documentation.md` - Comprehensive database schema documentation
- `README.md` - This file

### Configuration Templates
- `.env.example` - Template for environment variables
- `create_database.sql` - Database creation script
- `setup_complete.py` - Automated complete setup script

### Utility Scripts
- `test_connection.py` - Simple database connection test

## 🚀 Quick Start

### 1. Prerequisites
- PostgreSQL server installed and running
- Python packages: `sqlalchemy`, `psycopg2`, `pandas`

```bash
pip install sqlalchemy psycopg2 pandas
```

### 2. Database Setup

#### Option A: Secure Interactive Setup (Recommended)
```bash
cd sql
python setup_config.py
```

This will:
- Prompt for database credentials securely
- Create a `.env` file (excluded from Git)
- Test the database connection
- Set appropriate file permissions

#### Option B: Manual Configuration
1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` with your database credentials:
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_actual_password
POSTGRES_DATABASE=wuzzuf
```

3. Ensure `.env` has restricted permissions:
```bash
chmod 600 .env  # Unix/Linux/Mac only
```

### 3. Create Database and Schema

#### If database doesn't exist:
```sql
-- Connect to PostgreSQL as superuser and run:
CREATE DATABASE wuzzuf;
```

#### Create schema:
```bash
# Connect to wuzzuf database and run:
psql -U postgres -d wuzzuf -f schema.sql
```

### 4. Load Data

#### Option A: Automated Script (Recommended for testing)
```bash
python data_insertion.py
```

#### Option B: Manual Loading (Recommended for production)
For more control and reliability, use the manual process:
```bash
# Follow the step-by-step guide
cat MANUAL_DATA_LOADING.md
```

The manual approach:
- Gives you full control over each step
- Easier to troubleshoot issues
- Better for understanding the data structure
- More reliable for large datasets
- See `MANUAL_DATA_LOADING.md` for detailed instructions

## 🔍 Testing and Validation

### Test Database Connection
```bash
python test_connection.py
```

### Interactive Data Loading (Jupyter)
```bash
jupyter notebook ../notebooks/03_database_data_loading.ipynb
```

## 📊 Database Schema

The database uses a normalized relational schema with four main tables:

```
companies (company_id, company_name, industry, company_size)
    ↓
jobs (job_id, job_title, experience_level, city, salary_*, company_id)
    ↓
job_skills (job_id, skill_id)
    ↑
skills (skill_id, skill_name, skill_category)
```

See `schema_documentation.md` for detailed schema information.

## 🔒 Security Best Practices

### Environment Variables
- Database credentials are stored in `.env` file
- `.env` file is excluded from Git via `.gitignore`
- Passwords are never hardcoded in source code
- Interactive password prompts use `getpass` for security

### File Permissions
- `.env` file permissions set to 600 (owner read/write only)
- Sensitive files excluded from version control

### Connection Security
- Connection pooling with automatic cleanup
- Prepared statements to prevent SQL injection
- Transaction management with rollback capabilities

## 🐛 Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'sqlalchemy'"
```bash
pip install sqlalchemy psycopg2 pandas
```

#### "FATAL: password authentication failed"
- Check your PostgreSQL credentials
- Ensure PostgreSQL server is running
- Verify user permissions
- Run `python setup_config.py` to reconfigure

#### "database 'wuzzuf' does not exist"
```sql
-- Connect as superuser and create database:
CREATE DATABASE wuzzuf;
```

#### "relation 'companies' does not exist"
```bash
# Run schema creation:
psql -U postgres -d wuzzuf -f schema.sql
```

#### Permission denied on .env file
```bash
# Set correct permissions:
chmod 600 .env
```

### Getting Help

1. Check the logs in `data_insertion.log`
2. Run `python test_connection.py` to verify connectivity
3. Review the validation report in `data_insertion_report.txt`
4. Check PostgreSQL server logs

## 📈 Performance Notes

- Data insertion uses chunked processing for large datasets
- Indexes are optimized for common query patterns
- Connection pooling reduces overhead
- Transaction management ensures data consistency

## 🔄 Data Pipeline Flow

1. **Load CSV Data**: Read processed files from `../data/processed/`
2. **Extract Companies**: Deduplicate company information
3. **Insert Companies**: Bulk insert with error handling
4. **Insert Skills**: Load normalized skills data
5. **Create Mappings**: Map company names and skill IDs
6. **Insert Jobs**: Load job data with foreign key relationships
7. **Insert Job-Skills**: Create many-to-many relationships
8. **Validate Integrity**: Check foreign keys and data quality
9. **Generate Report**: Comprehensive validation summary

## 📝 Logging

All operations are logged to:
- Console output (INFO level)
- `data_insertion.log` file (detailed logging)
- `data_insertion_report.txt` (validation summary)

## 🎯 Next Steps

After successful data loading:
1. Run analytical queries using the provided views
2. Use the database for visualization and reporting
3. Implement additional analysis scripts
4. Set up regular data updates if needed