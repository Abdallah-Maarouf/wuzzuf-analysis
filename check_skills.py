#!/usr/bin/env python3
"""
Check skills data structure
"""

import sys
sys.path.append('sql')
from database_setup import DatabaseManager
import pandas as pd

def check_skills_data():
    try:
        db_manager = DatabaseManager()
        engine = db_manager.get_engine()
        
        print("Skills table structure:")
        skills_structure = pd.read_sql("SELECT * FROM skills LIMIT 5", engine)
        print(skills_structure)
        
        print("\nSkill categories available:")
        categories = pd.read_sql("SELECT DISTINCT skill_category FROM skills WHERE skill_category IS NOT NULL", engine)
        print(categories)
        
        print("\nSample skills data:")
        sample_skills = pd.read_sql("SELECT skill_name, skill_category FROM skills WHERE skill_name IS NOT NULL LIMIT 10", engine)
        print(sample_skills)
        
        print("\nSkills count by category:")
        category_counts = pd.read_sql("SELECT skill_category, COUNT(*) as count FROM skills GROUP BY skill_category", engine)
        print(category_counts)
        
        db_manager.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_skills_data()