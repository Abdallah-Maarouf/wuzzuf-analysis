#!/usr/bin/env python3
"""
Complete database setup script for Wuzzuf Job Market Analysis
This script handles database creation, schema setup, and connection testing
"""

import os
import sys
import subprocess
from database_setup import DatabaseManager, setup_database
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_postgresql_running():
    """Check if PostgreSQL service is running"""
    try:
        # Try to connect to default postgres database
        import psycopg2
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password=os.getenv('POSTGRES_PASSWORD', ''),
            database='postgres'
        )
        conn.close()
        return True
    except:
        return False

def run_sql_script(script_path, database='postgres', username='postgres', password=None):
    """Run SQL script using psql command line tool"""
    try:
        if not password:
            password = os.getenv('POSTGRES_PASSWORD') or input(f"Enter password for user '{username}': ")
        
        # Set environment variable for password
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        cmd = [
            'psql',
            '-h', 'localhost',
            '-p', '5432',
            '-U', username,
            '-d', database,
            '-f', script_path
        ]
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Successfully executed {script_path}")
            return True
        else:
            logger.error(f"Error executing {script_path}: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to run SQL script {script_path}: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Wuzzuf Job Market Analysis - Complete Database Setup")
    print("=" * 60)
    
    # Step 1: Check PostgreSQL
    print("\n1️⃣ Checking PostgreSQL service...")
    if not check_postgresql_running():
        print("❌ PostgreSQL is not running or not accessible")
        print("Please ensure PostgreSQL is installed and running on localhost:5432")
        print("Default user 'postgres' should be available")
        return False
    print("✅ PostgreSQL is running")
    
    # Step 2: Get connection parameters
    print("\n2️⃣ Database connection setup...")
    host = input("Enter PostgreSQL host (default: localhost): ").strip() or 'localhost'
    port = input("Enter PostgreSQL port (default: 5432): ").strip() or '5432'
    username = input("Enter PostgreSQL username (default: postgres): ").strip() or 'postgres'
    
    try:
        port = int(port)
    except ValueError:
        print("Invalid port number, using default 5432")
        port = 5432
    
    # Step 3: Create database
    print("\n3️⃣ Creating database 'wuzzuf'...")
    
    # Try using the Python approach first
    db_manager = DatabaseManager(host, port, username, database='wuzzuf')
    if db_manager.create_database():
        print("✅ Database 'wuzzuf' created successfully")
    else:
        print("⚠️ Could not create database using Python approach")
        print("Trying alternative method...")
        
        # Try using psql command
        if os.path.exists('sql/create_database.sql'):
            if run_sql_script('sql/create_database.sql', 'postgres', username):
                print("✅ Database created using SQL script")
            else:
                print("❌ Failed to create database")
                print("Please create the database manually:")
                print("  psql -U postgres -c 'CREATE DATABASE wuzzuf;'")
                return False
        else:
            print("❌ Database creation script not found")
            return False
    
    # Step 4: Create schema
    print("\n4️⃣ Creating database schema...")
    if not db_manager.create_schema('sql/schema.sql'):
        print("❌ Failed to create schema")
        print("Trying alternative method...")
        
        # Try using psql command
        if run_sql_script('sql/schema.sql', 'wuzzuf', username):
            print("✅ Schema created using SQL script")
        else:
            print("❌ Failed to create schema")
            return False
    else:
        print("✅ Schema created successfully")
    
    # Step 5: Test connection and display info
    print("\n5️⃣ Testing database connection...")
    status = db_manager.test_connection()
    
    if status['status'] == 'connected':
        print("✅ Database connection test successful!")
        print(f"\n📊 Database Information:")
        print(f"   Database: {status['database']}")
        print(f"   Tables created: {status['table_count']}")
        print(f"   PostgreSQL version: {status['version'][:80]}...")
        
        # Display table structure
        print(f"\n📋 Database Schema:")
        table_info = db_manager.get_table_info()
        if not table_info.empty:
            for table in ['companies', 'skills', 'jobs', 'job_skills']:
                if table in table_info['table_name'].values:
                    print(f"\n   🗂️ {table}:")
                    table_cols = table_info[table_info['table_name'] == table]
                    for _, col in table_cols.head(5).iterrows():  # Show first 5 columns
                        nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                        print(f"      - {col['column_name']}: {col['data_type']} {nullable}")
                    if len(table_cols) > 5:
                        print(f"      ... and {len(table_cols) - 5} more columns")
        
        print(f"\n🎉 Database setup completed successfully!")
        print(f"\n📝 Next steps:")
        print(f"   1. Run task 3.2 to load data into the database")
        print(f"   2. Use the DatabaseManager class in your Python scripts")
        print(f"   3. Connect using: postgresql://{username}:***@{host}:{port}/wuzzuf")
        
        db_manager.close()
        return True
        
    else:
        print(f"❌ Database connection test failed: {status.get('error')}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)