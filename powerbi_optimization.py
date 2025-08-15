# Power BI Data Optimization Script
# Optimizes CSV files for Power BI performance and creates data model documentation

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def optimize_for_powerbi():
    """Optimize data files for Power BI dashboard performance"""
    print("🚀 Starting Power BI Data Optimization")
    print("=" * 60)
    
    # Check if processed data exists
    processed_dir = Path('data/processed')
    if not processed_dir.exists():
        print("❌ data/processed directory not found")
        return
    
    # Create powerbi directory
    powerbi_dir = Path('powerbi')
    powerbi_dir.mkdir(exist_ok=True)
    
    # 1. Optimize jobs table
    print("\n🔧 Optimizing jobs table for Power BI...")
    try:
        jobs_df = pd.read_csv('data/processed/jobs.csv')
        
        # Data type optimizations
        if 'posting_date' in jobs_df.columns:
            jobs_df['posting_date'] = pd.to_datetime(jobs_df['posting_date'], errors='coerce')
        
        # Create categorical columns for better Power BI performance
        categorical_cols = [
            'job_title', 'position_type', 'position_level', 'experience_level',
            'city', 'country', 'pay_rate', 'currency', 'company_industry', 'company_size'
        ]
        
        for col in categorical_cols:
            if col in jobs_df.columns:
                jobs_df[col] = jobs_df[col].astype('category')
        
        # Add calculated columns for Power BI
        if 'salary_min' in jobs_df.columns and 'salary_max' in jobs_df.columns:
            jobs_df['salary_avg'] = (jobs_df['salary_min'] + jobs_df['salary_max']) / 2
            jobs_df['has_salary'] = (~jobs_df['salary_min'].isna()).astype('category')
        
        if 'posting_year' in jobs_df.columns and 'posting_month' in jobs_df.columns:
            jobs_df['posting_date_key'] = jobs_df['posting_year'] * 100 + jobs_df['posting_month']
            
            # Create month name for better visualization
            month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                          7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
            jobs_df['posting_month_name'] = jobs_df['posting_month'].map(month_names).astype('category')
        
        # Save optimized file
        jobs_df.to_csv('data/processed/jobs_powerbi.csv', index=False)
        print(f"✅ Optimized jobs table: {len(jobs_df):,} rows, {len(jobs_df.columns)} columns")
        
    except Exception as e:
        print(f"❌ Error optimizing jobs table: {e}")
        return
    
    # 2. Optimize skills table
    print("\n🔧 Optimizing skills table for Power BI...")
    try:
        skills_df = pd.read_csv('data/processed/skills.csv')
        
        # Data type optimizations
        if 'skill_name' in skills_df.columns:
            skills_df['skill_name'] = skills_df['skill_name'].astype('category')
        if 'skill_category' in skills_df.columns:
            skills_df['skill_category'] = skills_df['skill_category'].astype('category')
        
        # Add skill name length for analysis
        if 'skill_name' in skills_df.columns:
            skills_df['skill_name_length'] = skills_df['skill_name'].str.len()
        
        # Save optimized file
        skills_df.to_csv('data/processed/skills_powerbi.csv', index=False)
        print(f"✅ Optimized skills table: {len(skills_df):,} skills")
        
    except Exception as e:
        print(f"❌ Error optimizing skills table: {e}")
        return
    
    # 3. Optimize job_skills table
    print("\n🔧 Optimizing job_skills table for Power BI...")
    try:
        job_skills_df = pd.read_csv('data/processed/job_skills.csv')
        
        # Save optimized file (already optimized structure)
        job_skills_df.to_csv('data/processed/job_skills_powerbi.csv', index=False)
        print(f"✅ Optimized job_skills table: {len(job_skills_df):,} relationships")
        
    except Exception as e:
        print(f"❌ Error optimizing job_skills table: {e}")
        return
    
    # 4. Create aggregated datasets for performance
    print("\n📊 Creating aggregated datasets for dashboard performance...")
    
    try:
        # Skills summary
        skills_summary = (job_skills_df
                         .groupby('skill_id')
                         .size()
                         .reset_index(name='job_count')
                         .merge(skills_df[['skill_id', 'skill_name', 'skill_category']], on='skill_id')
                         .sort_values('job_count', ascending=False))
        
        skills_summary['percentage'] = (skills_summary['job_count'] / len(jobs_df) * 100).round(2)
        skills_summary.to_csv('data/processed/skills_summary_powerbi.csv', index=False)
        print(f"   ✓ Skills summary: {len(skills_summary)} skills")
        
        # Monthly trends summary
        if 'posting_year' in jobs_df.columns and 'posting_month' in jobs_df.columns:
            monthly_trends = (jobs_df
                             .groupby(['posting_year', 'posting_month'])
                             .size()
                             .reset_index(name='posting_count'))
            
            monthly_trends['year_month'] = (monthly_trends['posting_year'].astype(str) + '-' + 
                                           monthly_trends['posting_month'].astype(str).str.zfill(2))
            monthly_trends.to_csv('data/processed/monthly_trends_powerbi.csv', index=False)
            print(f"   ✓ Monthly trends: {len(monthly_trends)} periods")
        
        # Experience level summary
        if 'experience_level' in jobs_df.columns:
            experience_summary = (jobs_df
                                 .groupby('experience_level')
                                 .agg({
                                     'job_id': 'count',
                                     'salary_avg': 'mean' if 'salary_avg' in jobs_df.columns else 'applicants',
                                     'applicants': 'mean' if 'applicants' in jobs_df.columns else 'job_id'
                                 })
                                 .reset_index()
                                 .rename(columns={'job_id': 'job_count'}))
            
            experience_summary['percentage'] = (experience_summary['job_count'] / len(jobs_df) * 100).round(2)
            experience_summary.to_csv('data/processed/experience_summary_powerbi.csv', index=False)
            print(f"   ✓ Experience summary: {len(experience_summary)} levels")
        
        # Location summary
        if 'city' in jobs_df.columns and 'country' in jobs_df.columns:
            location_summary = (jobs_df
                               .groupby(['city', 'country'])
                               .size()
                               .reset_index(name='job_count')
                               .sort_values('job_count', ascending=False))
            
            location_summary['percentage'] = (location_summary['job_count'] / len(jobs_df) * 100).round(2)
            location_summary.to_csv('data/processed/location_summary_powerbi.csv', index=False)
            print(f"   ✓ Location summary: {len(location_summary)} locations")
        
        # Industry summary
        if 'company_industry' in jobs_df.columns:
            industry_summary = (jobs_df
                               .groupby('company_industry')
                               .agg({
                                   'job_id': 'count',
                                   'company_name': 'nunique' if 'company_name' in jobs_df.columns else 'job_id'
                               })
                               .reset_index()
                               .rename(columns={'job_id': 'job_count', 'company_name': 'company_count'}))
            
            industry_summary['percentage'] = (industry_summary['job_count'] / len(jobs_df) * 100).round(2)
            industry_summary = industry_summary.sort_values('job_count', ascending=False)
            industry_summary.to_csv('data/processed/industry_summary_powerbi.csv', index=False)
            print(f"   ✓ Industry summary: {len(industry_summary)} industries")
            
    except Exception as e:
        print(f"⚠️ Warning creating aggregated datasets: {e}")
    
    # 5. Create Power BI data model documentation
    print("\n📋 Creating Power BI data model documentation...")
    
    documentation = """# Power BI Data Model Documentation

## Overview
This document describes the optimized data model for the Wuzzuf Job Market Analysis Power BI dashboard.

## Main Tables

### 1. jobs_powerbi.csv (Fact Table)
- **Description:** Main fact table containing job posting details
- **Rows:** ~25,000 job postings
- **Key Columns:**
  - `job_id` (Primary Key): Unique identifier
  - `posting_date`: Date when job was posted
  - `job_title`: Standardized job title
  - `experience_level`: Entry/Mid/Senior categorization
  - `city`, `country`: Location information
  - `salary_min`, `salary_max`, `salary_avg`: Compensation data
  - `company_name`, `company_industry`: Company information

### 2. skills_powerbi.csv (Dimension Table)
- **Description:** Master list of skills with categories
- **Rows:** ~167 unique skills
- **Key Columns:**
  - `skill_id` (Primary Key): Unique identifier
  - `skill_name`: Standardized skill name
  - `skill_category`: Technical/Soft skill classification

### 3. job_skills_powerbi.csv (Bridge Table)
- **Description:** Many-to-many relationship between jobs and skills
- **Rows:** ~160,000 job-skill relationships
- **Key Columns:**
  - `job_id` (Foreign Key): Links to jobs table
  - `skill_id` (Foreign Key): Links to skills table

## Pre-Aggregated Tables (For Performance)
- `skills_summary_powerbi.csv`: Pre-calculated skill demand statistics
- `monthly_trends_powerbi.csv`: Pre-calculated monthly posting trends
- `experience_summary_powerbi.csv`: Pre-calculated experience level statistics
- `location_summary_powerbi.csv`: Pre-calculated location statistics
- `industry_summary_powerbi.csv`: Pre-calculated industry statistics

## Recommended Relationships in Power BI

```
jobs_powerbi (1) ←→ (*) job_skills_powerbi ←→ (*) (1) skills_powerbi
```

**Relationship Setup:**
1. jobs_powerbi[job_id] ←→ job_skills_powerbi[job_id] (One-to-Many)
2. skills_powerbi[skill_id] ←→ job_skills_powerbi[skill_id] (One-to-Many)

## Import Instructions

1. **Import Order:**
   - Import skills_powerbi.csv first (dimension table)
   - Import jobs_powerbi.csv second (fact table)
   - Import job_skills_powerbi.csv third (bridge table)
   - Import summary tables for performance dashboards

2. **Establish Relationships:**
   - Create relationships as documented above
   - Ensure cardinality is set correctly (1:*)
   - Use single cross-filter direction

3. **Data Type Validation:**
   - Ensure job_id and skill_id are recognized as whole numbers
   - Ensure posting_date is recognized as date/time
   - Categorical fields should be text type

## Dashboard Performance Tips

1. Use pre-aggregated summary tables for overview cards
2. Limit data import with date range filters if needed
3. Use the recommended relationship structure
4. Import only necessary columns for your dashboard

## Data Quality Notes

- **Salary Data:** ~70% of records may have missing salary information
- **Location Data:** Some records have "Unknown" city values
- **Skills Data:** All jobs have at least one skill assigned

## File Sizes (Approximate)
- jobs_powerbi.csv: ~8MB
- skills_powerbi.csv: ~5KB
- job_skills_powerbi.csv: ~4MB
- Summary tables: <1MB each
"""
    
    # Save documentation
    with open('powerbi/data_model_documentation.md', 'w', encoding='utf-8') as f:
        f.write(documentation)
    print("✅ Data model documentation saved: powerbi/data_model_documentation.md")
    
    # 6. Create import validation checklist
    checklist = """# Power BI Import Validation Checklist

## Pre-Import Validation
- [ ] All CSV files are present in data/processed/ directory
- [ ] Files are not corrupted (can open in Excel/text editor)
- [ ] File sizes are reasonable (jobs_powerbi.csv ~8MB)

## Import Process
- [ ] Import skills_powerbi.csv first (~167 rows)
- [ ] Import jobs_powerbi.csv second (~25,000 rows)
- [ ] Import job_skills_powerbi.csv third (~160,000 rows)

## Relationship Setup
- [ ] Create relationship: jobs_powerbi[job_id] ←→ job_skills_powerbi[job_id]
  - Cardinality: One to Many (1:*)
  - Cross filter direction: Single
  
- [ ] Create relationship: skills_powerbi[skill_id] ←→ job_skills_powerbi[skill_id]
  - Cardinality: One to Many (1:*)
  - Cross filter direction: Single

## Data Validation
- [ ] Total job count matches across tables (~25,000)
- [ ] Skill count matches (~167 unique skills)
- [ ] Date range is reasonable
- [ ] No circular relationships detected
- [ ] Sample data looks correct in data view

## Performance Validation
- [ ] Tables load quickly in data view
- [ ] Relationships work correctly
- [ ] No performance warnings in Power BI

## Final Validation
- [ ] Create test visual with job count by experience level
- [ ] Create test visual with top skills
- [ ] Verify filters work across visuals
- [ ] Save and test dashboard performance
"""
    
    with open('powerbi/import_validation_checklist.md', 'w', encoding='utf-8') as f:
        f.write(checklist)
    print("✅ Import validation checklist saved: powerbi/import_validation_checklist.md")
    
    print("\n" + "=" * 60)
    print("✅ Power BI Data Optimization Complete!")
    print("=" * 60)
    
    # List created files
    print("\n📁 Optimized Files Created:")
    optimized_files = [
        'jobs_powerbi.csv',
        'skills_powerbi.csv', 
        'job_skills_powerbi.csv',
        'skills_summary_powerbi.csv',
        'monthly_trends_powerbi.csv',
        'experience_summary_powerbi.csv',
        'location_summary_powerbi.csv',
        'industry_summary_powerbi.csv'
    ]
    
    for file in optimized_files:
        file_path = Path(f'data/processed/{file}')
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"   ✓ {file} ({size_mb:.2f} MB)")
    
    print("\n📋 Documentation Created:")
    print("   ✓ powerbi/data_model_documentation.md")
    print("   ✓ powerbi/import_validation_checklist.md")
    
    print("\n🎯 Next Steps:")
    print("   1. Open Power BI Desktop")
    print("   2. Import optimized CSV files from data/processed/")
    print("   3. Follow import validation checklist")
    print("   4. Create dashboard using data model documentation")

if __name__ == "__main__":
    optimize_for_powerbi()