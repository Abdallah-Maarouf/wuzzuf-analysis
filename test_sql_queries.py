#!/usr/bin/env python3
"""
Test SQL queries from analysis_queries.sql file
"""

import sys
import os
sys.path.append('sql')

from database_setup import DatabaseManager
import pandas as pd

def test_sql_queries():
    """Test all SQL queries from the analysis_queries.sql file"""
    
    print("🔍 Testing SQL Queries from analysis_queries.sql")
    print("=" * 60)
    
    try:
        # Initialize database connection
        db_manager = DatabaseManager()
        engine = db_manager.get_engine()
        
        # Read the SQL file
        with open('sql/analysis_queries.sql', 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Extract individual queries (split by comments and empty lines)
        queries = []
        current_query = []
        lines = sql_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('--') or line == '':
                if current_query and any(q.strip() for q in current_query):
                    query_text = '\n'.join(current_query).strip()
                    if query_text and 'SELECT' in query_text.upper():
                        queries.append(query_text)
                current_query = []
            else:
                current_query.append(line)
        
        # Add the last query if exists
        if current_query and any(q.strip() for q in current_query):
            query_text = '\n'.join(current_query).strip()
            if query_text and 'SELECT' in query_text.upper():
                queries.append(query_text)
        
        print(f"Found {len(queries)} SQL queries to test\n")
        
        # Test each query
        for i, query in enumerate(queries, 1):
            print(f"📊 Testing Query {i}:")
            print("-" * 40)
            
            try:
                # Execute query
                result_df = pd.read_sql(query, engine)
                print(f"✅ Query executed successfully")
                print(f"📈 Results: {len(result_df)} rows, {len(result_df.columns)} columns")
                
                # Show first few rows
                if len(result_df) > 0:
                    print("\nSample Results:")
                    if len(result_df) <= 3:
                        print(result_df.to_string(index=False))
                    else:
                        print(result_df.head(3).to_string(index=False))
                        print(f"... and {len(result_df) - 3} more rows")
                else:
                    print("No results returned")
                    
            except Exception as e:
                print(f"❌ Query failed: {e}")
            
            print("\n" + "=" * 60 + "\n")
        
        # Close database connection
        db_manager.close()
        
        print("✅ All SQL queries tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing SQL queries: {e}")
        return False

if __name__ == "__main__":
    success = test_sql_queries()
    if success:
        print("\n🎉 SQL query testing completed!")
    else:
        print("\n💥 SQL query testing failed!")