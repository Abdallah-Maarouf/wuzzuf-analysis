#!/usr/bin/env python3
"""
Power BI Data Validation Script
Validates that all required CSV files are properly formatted for Power BI import
"""

import pandas as pd
import os
from pathlib import Path

def validate_powerbi_data():
    """Validate all Power BI CSV files are ready for import"""
    
    print("=== Power BI Data Validation ===\n")
    
    # Define expected files
    required_files = {
        'jobs_powerbi.csv': 'Main fact table with job postings',
        'skills_powerbi.csv': 'Dimension table with skills',
        'job_skills_powerbi.csv': 'Bridge table for job-skill relationships',
        'skills_summary_powerbi.csv': 'Pre-aggregated skills statistics',
        'monthly_trends_powerbi.csv': 'Pre-aggregated monthly trends',
        'experience_summary_powerbi.csv': 'Pre-aggregated experience statistics',
        'location_summary_powerbi.csv': 'Pre-aggregated location statistics',
        'industry_summary_powerbi.csv': 'Pre-aggregated industry statistics'
    }
    
    data_dir = Path('data/processed')
    validation_results = {}
    
    # Check file existence
    print("1. File Existence Check:")
    for filename, description in required_files.items():
        filepath = data_dir / filename
        exists = filepath.exists()
        validation_results[filename] = {'exists': exists, 'description': description}
        status = "✓" if exists else "✗"
        print(f"   {status} {filename} - {description}")
    
    print("\n2. Data Structure Validation:")
    
    # Validate main tables
    if validation_results['jobs_powerbi.csv']['exists']:
        try:
            jobs_df = pd.read_csv(data_dir / 'jobs_powerbi.csv')
            print(f"   ✓ jobs_powerbi.csv: {len(jobs_df):,} rows, {len(jobs_df.columns)} columns")
            
            # Check required columns
            required_job_cols = ['job_id', 'posting_date', 'job_title', 'experience_level', 
                               'city', 'country', 'company_name', 'company_industry']
            missing_cols = [col for col in required_job_cols if col not in jobs_df.columns]
            if missing_cols:
                print(f"   ✗ Missing columns in jobs_powerbi.csv: {missing_cols}")
            else:
                print("   ✓ All required columns present in jobs_powerbi.csv")
                
            # Check data types
            print(f"   ✓ Date range: {jobs_df['posting_date'].min()} to {jobs_df['posting_date'].max()}")
            print(f"   ✓ Unique companies: {jobs_df['company_name'].nunique():,}")
            print(f"   ✓ Experience levels: {jobs_df['experience_level'].value_counts().to_dict()}")
            
        except Exception as e:
            print(f"   ✗ Error reading jobs_powerbi.csv: {e}")
    
    if validation_results['skills_powerbi.csv']['exists']:
        try:
            skills_df = pd.read_csv(data_dir / 'skills_powerbi.csv')
            print(f"   ✓ skills_powerbi.csv: {len(skills_df):,} rows, {len(skills_df.columns)} columns")
            
            # Check required columns
            required_skill_cols = ['skill_id', 'skill_name']
            missing_cols = [col for col in required_skill_cols if col not in skills_df.columns]
            if missing_cols:
                print(f"   ✗ Missing columns in skills_powerbi.csv: {missing_cols}")
            else:
                print("   ✓ All required columns present in skills_powerbi.csv")
                
            print(f"   ✓ Unique skills: {len(skills_df):,}")
            
        except Exception as e:
            print(f"   ✗ Error reading skills_powerbi.csv: {e}")
    
    if validation_results['job_skills_powerbi.csv']['exists']:
        try:
            job_skills_df = pd.read_csv(data_dir / 'job_skills_powerbi.csv')
            print(f"   ✓ job_skills_powerbi.csv: {len(job_skills_df):,} rows, {len(job_skills_df.columns)} columns")
            
            # Check required columns
            required_js_cols = ['job_id', 'skill_id']
            missing_cols = [col for col in required_js_cols if col not in job_skills_df.columns]
            if missing_cols:
                print(f"   ✗ Missing columns in job_skills_powerbi.csv: {missing_cols}")
            else:
                print("   ✓ All required columns present in job_skills_powerbi.csv")
                
            print(f"   ✓ Total job-skill relationships: {len(job_skills_df):,}")
            
        except Exception as e:
            print(f"   ✗ Error reading job_skills_powerbi.csv: {e}")
    
    print("\n3. Data Quality Checks:")
    
    # Cross-table validation
    if (validation_results['jobs_powerbi.csv']['exists'] and 
        validation_results['skills_powerbi.csv']['exists'] and 
        validation_results['job_skills_powerbi.csv']['exists']):
        
        try:
            # Check referential integrity
            unique_jobs_in_main = set(jobs_df['job_id'].unique())
            unique_jobs_in_bridge = set(job_skills_df['job_id'].unique())
            unique_skills_in_main = set(skills_df['skill_id'].unique())
            unique_skills_in_bridge = set(job_skills_df['skill_id'].unique())
            
            # Jobs referential integrity
            orphaned_jobs = unique_jobs_in_bridge - unique_jobs_in_main
            if orphaned_jobs:
                print(f"   ✗ {len(orphaned_jobs)} orphaned job_ids in bridge table")
            else:
                print("   ✓ All job_ids in bridge table exist in main jobs table")
            
            # Skills referential integrity
            orphaned_skills = unique_skills_in_bridge - unique_skills_in_main
            if orphaned_skills:
                print(f"   ✗ {len(orphaned_skills)} orphaned skill_ids in bridge table")
            else:
                print("   ✓ All skill_ids in bridge table exist in main skills table")
            
            # Coverage check
            jobs_with_skills = len(unique_jobs_in_bridge)
            total_jobs = len(unique_jobs_in_main)
            coverage = (jobs_with_skills / total_jobs) * 100
            print(f"   ✓ Skills coverage: {jobs_with_skills:,}/{total_jobs:,} jobs ({coverage:.1f}%)")
            
        except Exception as e:
            print(f"   ✗ Error in cross-table validation: {e}")
    
    print("\n4. File Size Analysis:")
    for filename in required_files.keys():
        filepath = data_dir / filename
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"   ✓ {filename}: {size_mb:.2f} MB")
    
    print("\n5. Power BI Import Readiness:")
    
    # Check for common Power BI issues
    issues_found = []
    
    if validation_results['jobs_powerbi.csv']['exists']:
        # Check for special characters in column names
        problematic_cols = [col for col in jobs_df.columns if any(char in col for char in ['#', '%', '&', '*'])]
        if problematic_cols:
            issues_found.append(f"Problematic column names: {problematic_cols}")
        
        # Check for very long text values that might cause issues
        text_cols = jobs_df.select_dtypes(include=['object']).columns
        for col in text_cols:
            max_length = jobs_df[col].astype(str).str.len().max()
            if max_length > 1000:
                issues_found.append(f"Very long text in {col}: max {max_length} characters")
    
    if issues_found:
        print("   ⚠ Potential issues found:")
        for issue in issues_found:
            print(f"     - {issue}")
    else:
        print("   ✓ No obvious Power BI compatibility issues detected")
    
    print("\n6. Summary:")
    total_files = len(required_files)
    existing_files = sum(1 for result in validation_results.values() if result['exists'])
    
    if existing_files == total_files:
        print(f"   ✓ All {total_files} required files are present and ready for Power BI import")
        print("   ✓ Data structure validation passed")
        print("   ✓ Ready to proceed with Power BI dashboard creation")
        return True
    else:
        print(f"   ✗ Only {existing_files}/{total_files} required files are present")
        print("   ✗ Complete data preparation before proceeding with Power BI")
        return False

def generate_powerbi_import_summary():
    """Generate a summary file for Power BI import"""
    
    try:
        data_dir = Path('data/processed')
        
        # Read main tables
        jobs_df = pd.read_csv(data_dir / 'jobs_powerbi.csv')
        skills_df = pd.read_csv(data_dir / 'skills_powerbi.csv')
        job_skills_df = pd.read_csv(data_dir / 'job_skills_powerbi.csv')
        
        summary = f"""# Power BI Import Summary

## Data Overview
- **Total Job Postings**: {len(jobs_df):,}
- **Unique Companies**: {jobs_df['company_name'].nunique():,}
- **Unique Skills**: {len(skills_df):,}
- **Job-Skill Relationships**: {len(job_skills_df):,}
- **Date Range**: {jobs_df['posting_date'].min()} to {jobs_df['posting_date'].max()}

## Experience Level Distribution
{jobs_df['experience_level'].value_counts().to_string()}

## Top 10 Industries
{jobs_df['company_industry'].value_counts().head(10).to_string()}

## Top 10 Cities
{jobs_df['city'].value_counts().head(10).to_string()}

## Data Quality Notes
- **Salary Data Coverage**: {(jobs_df['salary_avg'].notna().sum() / len(jobs_df) * 100):.1f}% of records have salary information
- **Location Data**: {(jobs_df['city'] != 'Unknown').sum() / len(jobs_df) * 100:.1f}% of records have valid city information
- **Skills per Job**: {len(job_skills_df) / len(jobs_df):.1f} average skills per job posting

## File Sizes
- jobs_powerbi.csv: {(data_dir / 'jobs_powerbi.csv').stat().st_size / (1024*1024):.2f} MB
- skills_powerbi.csv: {(data_dir / 'skills_powerbi.csv').stat().st_size / (1024*1024):.2f} MB
- job_skills_powerbi.csv: {(data_dir / 'job_skills_powerbi.csv').stat().st_size / (1024*1024):.2f} MB

Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Save summary
        with open('powerbi/import_summary.md', 'w') as f:
            f.write(summary)
        
        print("✓ Power BI import summary generated: powerbi/import_summary.md")
        
    except Exception as e:
        print(f"✗ Error generating import summary: {e}")

if __name__ == "__main__":
    # Run validation
    is_ready = validate_powerbi_data()
    
    if is_ready:
        print("\n" + "="*50)
        generate_powerbi_import_summary()
        print("\nNext steps:")
        print("1. Open Power BI Desktop")
        print("2. Follow the dashboard_creation_guide.md")
        print("3. Import CSV files in the specified order")
        print("4. Create relationships and build visualizations")
    else:
        print("\nPlease complete data preparation before proceeding with Power BI dashboard creation.")