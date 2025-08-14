"""
Database connection utilities and setup for Wuzzuf Job Market Analysis
Provides database connection management, schema creation, and utility functions
"""

import os
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import logging
from typing import Optional, Dict, Any
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages PostgreSQL database connections and operations for the Wuzzuf analysis project
    """
    
    def __init__(self, 
                 host: str = 'localhost',
                 port: int = 5432,
                 username: str = 'postgres',
                 password: str = None,
                 database: str = 'wuzzuf'):
        """
        Initialize database manager with connection parameters
        
        Args:
            host: Database host (default: localhost)
            port: Database port (default: 5432)
            username: Database username (default: postgres)
            password: Database password (will prompt if None)
            database: Database name (default: wuzzuf)
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password or os.getenv('POSTGRES_PASSWORD')
        self.database = database
        self.engine = None
        self.connection_string = None
        
    def _build_connection_string(self, database: str = None) -> str:
        """Build PostgreSQL connection string"""
        db_name = database or self.database
        if not self.password:
            self.password = input(f"Enter password for PostgreSQL user '{self.username}': ")
        
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{db_name}"
    
    def create_database(self) -> bool:
        """
        Create the wuzzuf database if it doesn't exist
        
        Returns:
            bool: True if database was created or already exists, False otherwise
        """
        try:
            # Connect to default postgres database to create wuzzuf database
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                database='postgres'
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Simple approach: try to create database, ignore if exists
            try:
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.database)))
                logger.info(f"Database '{self.database}' created successfully")
            except psycopg2.errors.DuplicateDatabase:
                logger.info(f"Database '{self.database}' already exists")
            
            cursor.close()
            conn.close()
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Error creating database: {e}")
            return False
    
    def get_engine(self, retry_count: int = 3, retry_delay: int = 2):
        """
        Get SQLAlchemy engine with connection retry logic
        
        Args:
            retry_count: Number of connection attempts
            retry_delay: Delay between retry attempts in seconds
            
        Returns:
            SQLAlchemy engine object
        """
        if self.engine is None:
            self.connection_string = self._build_connection_string()
            
            for attempt in range(retry_count):
                try:
                    self.engine = create_engine(
                        self.connection_string,
                        pool_size=10,
                        max_overflow=20,
                        pool_pre_ping=True,
                        pool_recycle=3600
                    )
                    
                    # Test connection
                    with self.engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                    
                    logger.info("Database connection established successfully")
                    break
                    
                except SQLAlchemyError as e:
                    logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                    if attempt < retry_count - 1:
                        time.sleep(retry_delay)
                    else:
                        logger.error("All connection attempts failed")
                        raise
        
        return self.engine
    
    def execute_sql_file(self, file_path: str) -> bool:
        """
        Execute SQL commands from a file
        
        Args:
            file_path: Path to SQL file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sql_content = file.read()
            
            engine = self.get_engine()
            with engine.connect() as conn:
                # Split by semicolon and execute each statement
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                
                for statement in statements:
                    if statement:
                        conn.execute(text(statement))
                        
                conn.commit()
            
            logger.info(f"Successfully executed SQL file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error executing SQL file {file_path}: {e}")
            return False
    
    def create_schema(self, schema_file: str = 'sql/schema.sql') -> bool:
        """
        Create database schema from SQL file
        
        Args:
            schema_file: Path to schema SQL file
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Creating database schema...")
        return self.execute_sql_file(schema_file)
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test database connection and return status information
        
        Returns:
            Dict with connection status and database information
        """
        try:
            engine = self.get_engine()
            with engine.connect() as conn:
                # Get database version
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                
                # Get table count
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                table_count = result.fetchone()[0]
                
                return {
                    'status': 'connected',
                    'database': self.database,
                    'version': version,
                    'table_count': table_count,
                    'connection_string': self.connection_string.replace(self.password, '***')
                }
                
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'database': self.database
            }
    
    def get_table_info(self) -> pd.DataFrame:
        """
        Get information about all tables in the database
        
        Returns:
            DataFrame with table information
        """
        try:
            engine = self.get_engine()
            query = """
            SELECT 
                table_name,
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
            """
            
            return pd.read_sql(query, engine)
            
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            return pd.DataFrame()
    
    def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            logger.info("Database connections closed")


def setup_database(host='localhost', port=5432, username='postgres', password=None):
    """
    Complete database setup function
    
    Args:
        host: Database host
        port: Database port  
        username: Database username
        password: Database password
        
    Returns:
        DatabaseManager instance if successful, None otherwise
    """
    try:
        # Initialize database manager
        db_manager = DatabaseManager(host, port, username, password)
        
        # Create database
        if not db_manager.create_database():
            logger.error("Failed to create database")
            return None
        
        # Create schema
        if not db_manager.create_schema():
            logger.error("Failed to create schema")
            return None
        
        # Test connection
        status = db_manager.test_connection()
        if status['status'] == 'connected':
            logger.info("Database setup completed successfully")
            logger.info(f"Tables created: {status['table_count']}")
            return db_manager
        else:
            logger.error(f"Database connection test failed: {status.get('error')}")
            return None
            
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return None


if __name__ == "__main__":
    """
    Run database setup when script is executed directly
    """
    print("Wuzzuf Job Market Analysis - Database Setup")
    print("=" * 50)
    
    # Get connection parameters
    host = input("Enter PostgreSQL host (default: localhost): ").strip() or 'localhost'
    port = input("Enter PostgreSQL port (default: 5432): ").strip() or '5432'
    username = input("Enter PostgreSQL username (default: postgres): ").strip() or 'postgres'
    
    try:
        port = int(port)
    except ValueError:
        print("Invalid port number, using default 5432")
        port = 5432
    
    # Setup database
    db_manager = setup_database(host, port, username)
    
    if db_manager:
        print("\n✅ Database setup completed successfully!")
        
        # Display connection info
        status = db_manager.test_connection()
        print(f"\nDatabase: {status['database']}")
        print(f"Tables created: {status['table_count']}")
        print(f"PostgreSQL version: {status['version'][:50]}...")
        
        # Display table structure
        print("\nTable structure:")
        table_info = db_manager.get_table_info()
        if not table_info.empty:
            for table in table_info['table_name'].unique():
                print(f"\n📋 {table}:")
                table_cols = table_info[table_info['table_name'] == table]
                for _, col in table_cols.iterrows():
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    print(f"  - {col['column_name']}: {col['data_type']} {nullable}")
        
        db_manager.close()
    else:
        print("\n❌ Database setup failed!")