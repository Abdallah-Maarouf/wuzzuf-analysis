#!/usr/bin/env python3
"""
Debug script to check skills data structure
"""

import sys
sys.path.append('sql')
from database_setup import DatabaseManager
import pandas as pd

def debug_skills():
    try:
        db_manager = DatabaseManager()
        engine = db_manager.get_engine()
        
        print("=== DEBUGGING SKILLS DATA ===")
        
        # Check what skill categories actually exist
        print("\n1. Skill Categories in Database:")
        category_check = """
        SELECT 
            skill_category,
            COUNT(*) as count
        FROM skills 
        WHERE skill_category IS NOT NULL
        GROUP BY skill_category
        ORDER BY count DESC;
        """
        
        result = pd.read_sql(category_check, engine)
        print(result)
        
        # Check for NULL categories
        print("\n2. NULL Category Count:")
        null_check = "SELECT COUNT(*) as null_count FROM skills WHERE skill_category IS NULL;"
        null_result = pd.read_sql(null_check, engine)
        print(f"Skills with NULL category: {null_result['null_count'].iloc[0]}")
        
        # Check sample skills data
        print("\n3. Sample Skills Data:")
        sample_skills = """
        SELECT skill_name, skill_category
        FROM skills 
        WHERE skill_name IS NOT NULL 
        LIMIT 10;
        """
        
        sample = pd.read_sql(sample_skills, engine)
        print(sample)
        
        # Try a general skills query without category filter
        print("\n4. Top 10 Skills (No Category Filter):")
        general_skills = """
        SELECT 
            s.skill_name,
            s.skill_category,
            COUNT(js.job_id) as job_count
        FROM skills s
        JOIN job_skills js ON s.skill_id = js.skill_id
        WHERE s.skill_name IS NOT NULL 
            AND s.skill_name != ''
        GROUP BY s.skill_name, s.skill_category
        ORDER BY job_count DESC
        LIMIT 10;
        """
        
        general_result = pd.read_sql(general_skills, engine)
        print(general_result)
        
        db_manager.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_skills()