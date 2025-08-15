# Power BI Data Optimization Script
# Optimizes CSV files for Power BI performance and creates data model documentation

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class PowerBIDataOptimizer:
    """
    Optimizes data files for Power BI dashboard performance
    """
    
    def __init__(self, input_dir='../data/processed', output_dir='../data/processed'):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def optimize_jobs_table(self):
        """Optimize jobs table for Power BI performance"""
        print("🔧 Optimizing jobs table for Power BI...")
        
        # Load jobs data
        jobs_df = pd.read_csv(self.input_dir / 'jobs.csv')
        
        # Data type optimizations
        optimizations = {
            'job_id': 'int64',
            'posting_date': 'datetime64[ns]',
            'years_experience': 'Int8',  # Nullable integer
            'salary_min': 'float32',
            'salary_max': 'float32', 
            'applicants': 'float32',
            'posting_year': 'int16',
            'posting_month': 'int8'
        }
        
        # Apply optimizations
        for col, dtype in optimizations.items():
            if col in jobs_df.columns:
                if dtype.startswith('datetime'):
                    jobs_df[col] = pd.to_datetime(jobs_df[col], errors='coerce')
                else:
                    jobs_df[col] = jobs_df[col].astype(dtype, errors='ignore')
        
        # Create categorical columns for better Power BI performance
        categorical_cols = [
            'job_title', 'position_type', 'position_level', 'experience_level',
            'city', 'country', 'pay_rate', 'currency', 'company_industry', 'company_size'
        ]
        
        for col in categorical_cols:
            if col in jobs_df.columns:
                jobs_df[col] = jobs_df[col].astype('category')
        
        # Add calculated columns for Power BI
        jobs_df['salary_avg'] = (jobs_df['salary_min'] + jobs_df['salary_max']) / 2
        jobs_df['has_salary'] = (~jobs_df['salary_min'].isna()).astype('category')
        jobs_df['posting_date_key'] = jobs_df['posting_year'] * 100 + jobs_df['posting_month']
        
        # Create month name for better visualization
        month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                      7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        jobs_df['posting_month_name'] = jobs_df['posting_month'].map(month_names).astype('category')
        
        # Save optimized file
        output_file = self.output_dir / 'jobs_powerbi.csv'
        jobs_df.to_csv(output_file, index=False)
        
        print(f"✅ Optimized jobs table saved: {output_file}")
        print(f"   Original size: {len(jobs_df):,} rows")
        print(f"   Columns: {len(jobs_df.columns)}")
        
        return jobs_df
    
    def optimize_skills_table(self):
        """Optimize skills table for Power BI performance"""
        print("\n🔧 Optimizing skills table for Power BI...")
        
        # Load skills data
        skills_df = pd.read_csv(self.input_dir / 'skills.csv')
        
        # Data type optimizations
        skills_df['skill_id'] = skills_df['skill_id'].astype('int16')
        skills_df['skill_name'] = skills_df['skill_name'].astype('category')
        skills_df['skill_category'] = skills_df['skill_category'].astype('category')
        
        # Add skill name length for analysis
        skills_df['skill_name_length'] = skills_df['skill_name'].str.len().astype('int8')
        
        # Save optimized file
        output_file = self.output_dir / 'skills_powerbi.csv'
        skills_df.to_csv(output_file, index=False)
        
        print(f"✅ Optimized skills table saved: {output_file}")
        print(f"   Skills count: {len(skills_df):,}")
        
        return skills_df
    
    def optimize_job_skills_table(self):
        """Optimize job_skills table for Power BI performance"""
        print("\n🔧 Optimizing job_skills table for Power BI...")
        
        # Load job_skills data
        job_skills_df = pd.read_csv(self.input_dir / 'job_skills.csv')
        
        # Data type optimizations
        job_skills_df['job_id'] = job_skills_df['job_id'].astype('int64')
        job_skills_df['skill_id'] = job_skills_df['skill_id'].astype('int16')
        
        # Save optimized file
        output_file = self.output_dir / 'job_skills_powerbi.csv'
        job_skills_df.to_csv(output_file, index=False)
        
        print(f"✅ Optimized job_skills table saved: {output_file}")
        print(f"   Relationships: {len(job_skills_df):,}")
        
        return job_skills_df
    
    def create_aggregated_datasets(self, jobs_df, skills_df, job_skills_df):
        """Create pre-aggregated datasets for dashboard performance"""
        print("\n📊 Creating aggregated datasets for dashboard performance...")
        
        # 1. Skills summary for dashboard
        skills_summary = (job_skills_df
                         .groupby('skill_id')
                         .size()
                         .reset_index(name='job_count')
                         .merge(skills_df[['skill_id', 'skill_name', 'skill_category']], on='skill_id')
                         .sort_values('job_count', ascending=False))
        
        skills_summary['percentage'] = (skills_summary['job_count'] / len(jobs_df) * 100).round(2)
        skills_summary.to_csv(self.output_dir / 'skills_summary_powerbi.csv', index=False)
        print(f"   ✓ Skills summary: {len(skills_summary)} skills")
        
        # 2. Monthly trends summary
        monthly_trends = (jobs_df
                         .groupby(['posting_year', 'posting_month', 'posting_month_name'])
                         .size()
                         .reset_index(name='posting_count'))
        
        monthly_trends['year_month'] = (monthly_trends['posting_year'].astype(str) + '-' + 
                                       monthly_trends['posting_month'].astype(str).str.zfill(2))
        monthly_trends.to_csv(self.output_dir / 'monthly_trends_powerbi.csv', index=False)
        print(f"   ✓ Monthly trends: {len(monthly_trends)} periods")
        
        # 3. Experience level summary
        experience_summary = (jobs_df
                             .groupby('experience_level')
                             .agg({
                                 'job_id': 'count',
                                 'salary_avg': 'mean',
                                 'applicants': 'mean'
                             })
                             .reset_index()
                             .rename(columns={'job_id': 'job_count'}))
        
        experience_summary['percentage'] = (experience_summary['job_count'] / len(jobs_df) * 100).round(2)
        experience_summary.to_csv(self.output_dir / 'experience_summary_powerbi.csv', index=False)
        print(f"   ✓ Experience summary: {len(experience_summary)} levels")
        
        # 4. Location summary
        location_summary = (jobs_df
                           .groupby(['city', 'country'])
                           .size()
                           .reset_index(name='job_count')
                           .sort_values('job_count', ascending=False))
        
        location_summary['percentage'] = (location_summary['job_count'] / len(jobs_df) * 100).round(2)
        location_summary.to_csv(self.output_dir / 'location_summary_powerbi.csv', index=False)
        print(f"   ✓ Location summary: {len(location_summary)} locations")
        
        # 5. Company industry summary
        industry_summary = (jobs_df
                           .groupby('company_industry')
                           .agg({
                               'job_id': 'count',
                               'company_name': 'nunique',
                               'salary_avg': 'mean'
                           })
                           .reset_index()
                           .rename(columns={'job_id': 'job_count', 'company_name': 'company_count'}))
        
        industry_summary['percentage'] = (industry_summary['job_count'] / len(jobs_df) * 100).round(2)
        industry_summary = industry_summary.sort_values('job_count', ascending=False)
        industry_summary.to_csv(self.output_dir / 'industry_summary_powerbi.csv', index=False)
        print(f"   ✓ Industry summary: {len(industry_summary)} industries")
        
        return {
            'skills_summary': skills_summary,
            'monthly_trends': monthly_trends,
            'experience_summary': experience_summary,
            'location_summary': location_summary,
            'industry_summary': industry_summary
        }
    
    def create_data_model_documentation(self):
        """Create Power BI data model documentation"""
        print("\n📋 Creating Power BI data model documentation...")
        
        documentation = """# Power BI Data Model Documentation

## Overview
This document describes the optimized data model for the Wuzzuf Job Market Analysis Power BI dashboard.

## Tables and Relationships

### 1. jobs_powerbi.csv (Fact Table)
**Description:** Main fact table containing job posting details
**Rows:** ~25,000 job postings
**Key Columns:**
- `job_id` (Primary Key): Unique identifier for each job posting
- `posting_date`: Date when job was posted
- `job_title`: Standardized job title
- `experience_level`: Entry/Mid/Senior categorization
- `city`, `country`: Location information
- `salary_min`, `salary_max`, `salary_avg`: Compensation data
- `company_name`, `company_industry`: Company information
- `posting_year`, `posting_month`: Date components for time analysis

**Optimizations Applied:**
- Categorical data types for text fields
- Optimized numeric types (int8, int16, float32)
- Added calculated columns (salary_avg, has_salary)
- Date parsing and validation

### 2. skills_powerbi.csv (Dimension Table)
**Description:** Master list of skills with categories
**Rows:** ~167 unique skills
**Key Columns:**
- `skill_id` (Primary Key): Unique identifier for each skill
- `skill_name`: Standardized skill name
- `skill_category`: Technical/Soft skill classification

**Optimizations Applied:**
- Categorical data types for better performance
- Compact integer types for IDs

### 3. job_skills_powerbi.csv (Bridge Table)
**Description:** Many-to-many relationship between jobs and skills
**Rows:** ~160,000 job-skill relationships
**Key Columns:**
- `job_id` (Foreign Key): Links to jobs table
- `skill_id` (Foreign Key): Links to skills table

**Optimizations Applied:**
- Optimized integer types for foreign keys
- Minimal columns for performance

## Pre-Aggregated Tables (For Performance)

### 4. skills_summary_powerbi.csv
**Description:** Pre-calculated skill demand statistics
**Columns:** skill_id, skill_name, skill_category, job_count, percentage

### 5. monthly_trends_powerbi.csv
**Description:** Pre-calculated monthly posting trends
**Columns:** posting_year, posting_month, posting_month_name, posting_count, year_month

### 6. experience_summary_powerbi.csv
**Description:** Pre-calculated experience level statistics
**Columns:** experience_level, job_count, salary_avg, applicants, percentage

### 7. location_summary_powerbi.csv
**Description:** Pre-calculated location statistics
**Columns:** city, country, job_count, percentage

### 8. industry_summary_powerbi.csv
**Description:** Pre-calculated industry statistics
**Columns:** company_industry, job_count, company_count, salary_avg, percentage

## Recommended Relationships in Power BI

```
jobs_powerbi (1) ←→ (*) job_skills_powerbi ←→ (*) (1) skills_powerbi
```

**Relationship Details:**
1. jobs_powerbi[job_id] ←→ job_skills_powerbi[job_id] (One-to-Many)
2. skills_powerbi[skill_id] ←→ job_skills_powerbi[skill_id] (One-to-Many)

## Data Quality Notes

### Missing Data Handling:
- Salary data: ~70% of records have missing salary information
- Location data: Some records have "Unknown" city values
- Skills data: All jobs have at least one skill assigned

### Data Types Optimization:
- Text fields converted to categories for better compression
- Numeric fields optimized for size (int8, int16, float32)
- Date fields properly parsed and validated

## Dashboard Performance Tips

1. **Use Pre-Aggregated Tables:** For summary cards and overview charts
2. **Limit Data Import:** Consider date range filters if needed
3. **Optimize Relationships:** Use the recommended relationship structure
4. **Column Selection:** Import only necessary columns for your dashboard
5. **Data Refresh:** Set up incremental refresh if data updates regularly

## File Sizes (Approximate)
- jobs_powerbi.csv: ~8MB
- skills_powerbi.csv: ~5KB
- job_skills_powerbi.csv: ~4MB
- Summary tables: <1MB each

## Import Order Recommendation
1. Import skills_powerbi.csv first (dimension table)
2. Import jobs_powerbi.csv second (fact table)
3. Import job_skills_powerbi.csv third (bridge table)
4. Import summary tables for performance dashboards
5. Establish relationships as documented above

## Validation Checklist
- [ ] All tables imported successfully
- [ ] Relationships established correctly
- [ ] Data types recognized properly
- [ ] No circular relationships created
- [ ] Summary tables match detailed data
- [ ] Date fields formatted correctly
- [ ] Categorical fields showing proper values
"""
        
        # Save documentation
        doc_file = Path('../powerbi/data_model_documentation.md')
        doc_file.parent.mkdir(parents=True, exist_ok=True)
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(documentation)
        
        print(f"✅ Data model documentation saved: {doc_file}")
        
        return documentation
    
    def create_import_validation_checklist(self):
        """Create Power BI import validation checklist"""
        print("\n✅ Creating Power BI import validation checklist...")
        
        checklist = """# Power BI Data Import Validation Checklist

## Pre-Import Validation
- [ ] All CSV files are present in data/processed/ directory
- [ ] Files are not corrupted (can open in Excel/text editor)
- [ ] File sizes are reasonable (jobs_powerbi.csv ~8MB)
- [ ] No special characters in file names

## Import Process
- [ ] Import skills_powerbi.csv first
  - [ ] skill_id recognized as whole number
  - [ ] skill_name and skill_category as text
  - [ ] ~167 rows imported
  
- [ ] Import jobs_powerbi.csv second
  - [ ] job_id recognized as whole number
  - [ ] posting_date recognized as date
  - [ ] Categorical fields (job_title, city, etc.) as text
  - [ ] Numeric fields (salary_min, salary_max) as decimal
  - [ ] ~25,000 rows imported
  
- [ ] Import job_skills_powerbi.csv third
  - [ ] Both job_id and skill_id as whole numbers
  - [ ] ~160,000 rows imported

## Relationship Setup
- [ ] Create relationship: jobs_powerbi[job_id] ←→ job_skills_powerbi[job_id]
  - [ ] Cardinality: One to Many (1:*)
  - [ ] Cross filter direction: Single
  - [ ] Make this relationship active: Yes
  
- [ ] Create relationship: skills_powerbi[skill_id] ←→ job_skills_powerbi[skill_id]
  - [ ] Cardinality: One to Many (1:*)
  - [ ] Cross filter direction: Single
  - [ ] Make this relationship active: Yes

## Data Validation
- [ ] Total job count matches across tables (~25,000)
- [ ] Skill count matches (~167 unique skills)
- [ ] Date range is reasonable (check min/max posting_date)
- [ ] No circular relationships detected
- [ ] Sample data looks correct in data view

## Performance Validation
- [ ] Tables load quickly in data view
- [ ] Relationships work correctly (test with simple visual)
- [ ] No performance warnings in Power BI
- [ ] Memory usage is reasonable

## Summary Tables (Optional for Performance)
- [ ] Import skills_summary_powerbi.csv
- [ ] Import monthly_trends_powerbi.csv  
- [ ] Import experience_summary_powerbi.csv
- [ ] Import location_summary_powerbi.csv
- [ ] Import industry_summary_powerbi.csv

## Final Validation
- [ ] Create test visual with job count by experience level
- [ ] Create test visual with top skills
- [ ] Verify filters work across visuals
- [ ] Check that slicers affect multiple visuals
- [ ] Save and test dashboard performance

## Troubleshooting Common Issues

### Issue: Relationships not working
**Solution:** Check that key columns have matching data types and no null values

### Issue: Slow performance
**Solution:** Use pre-aggregated summary tables for overview visuals

### Issue: Date fields not recognized
**Solution:** Ensure posting_date column is formatted as Date in Power BI

### Issue: Categorical fields showing as numbers
**Solution:** Change data type to Text in Power Query Editor

### Issue: Missing data in visuals
**Solution:** Check relationship directions and active relationships

## Contact Information
For questions about this data model, refer to the project documentation or data model documentation.md file.
"""
        
        # Save checklist
        checklist_file = Path('../powerbi/import_validation_checklist.md')
        with open(checklist_file, 'w', encoding='utf-8') as f:
            f.write(checklist)
        
        print(f"✅ Import validation checklist saved: {checklist_file}")
        
        return checklist
    
    def run_optimization(self):
        """Run complete Power BI optimization process"""
        print("🚀 Starting Power BI Data Optimization")
        print("=" * 60)
        
        # Optimize main tables
        jobs_df = self.optimize_jobs_table()
        skills_df = self.optimize_skills_table()
        job_skills_df = self.optimize_job_skills_table()
        
        # Create aggregated datasets
        summaries = self.create_aggregated_datasets(jobs_df, skills_df, job_skills_df)
        
        # Create documentation
        self.create_data_model_documentation()
        self.create_import_validation_checklist()
        
        print("\n" + "=" * 60)
        print("✅ Power BI Data Optimization Complete!")
        print("=" * 60)
        
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
            file_path = self.output_dir / file
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"   ✓ {file} ({size_mb:.2f} MB)")
        
        print("\n📋 Documentation Created:")
        print("   ✓ data_model_documentation.md")
        print("   ✓ import_validation_checklist.md")
        
        print("\n🎯 Next Steps:")
        print("   1. Open Power BI Desktop")
        print("   2. Import optimized CSV files")
        print("   3. Follow import validation checklist")
        print("   4. Create dashboard using data model documentation")
        
        return {
            'jobs_df': jobs_df,
            'skills_df': skills_df,
            'job_skills_df': job_skills_df,
            'summaries': summaries
        }

if __name__ == "__main__":
    # Run optimization
    optimizer = PowerBIDataOptimizer()
    results = optimizer.run_optimization()