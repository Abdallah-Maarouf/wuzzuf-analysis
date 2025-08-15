# Power BI Data Model Documentation

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
