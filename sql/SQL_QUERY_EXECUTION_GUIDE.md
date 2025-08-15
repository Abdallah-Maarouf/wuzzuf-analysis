# SQL Query Execution Guide and Documentation

## Overview

This guide provides comprehensive documentation for executing and understanding the SQL queries used in the Wuzzuf Job Market Analysis project. All queries are designed to answer the 6 key business questions and provide actionable business intelligence insights.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Database Connection Setup](#database-connection-setup)
3. [Query Execution Instructions](#query-execution-instructions)
4. [Business Questions and Queries](#business-questions-and-queries)
5. [Query Validation](#query-validation)
6. [Expected Results](#expected-results)
7. [Troubleshooting](#troubleshooting)
8. [Performance Optimization](#performance-optimization)

## Prerequisites

### Required Software
- PostgreSQL 12+ installed and running
- Python 3.8+ with required packages:
  - `pandas`
  - `sqlalchemy`
  - `psycopg2-binary`
  - `python-dotenv`

### Database Setup
Ensure the Wuzzuf database is properly set up with all tables populated:
- `jobs` table: 25,114 records
- `companies` table: 4,468 records  
- `skills` table: 167 records
- `job_skills` table: 159,894 records

## Database Connection Setup

### Method 1: Using Python Database Manager

```python
import sys
sys.path.append('../sql')
from database_setup import DatabaseManager

# Initialize connection
db_manager = DatabaseManager()
engine = db_manager.get_engine()

# Test connection
status = db_manager.test_connection()
print(f"Connected to database: {status['database']}")
```

### Method 2: Direct SQL Connection

```python
import pandas as pd
from sqlalchemy import create_engine

# Connection string (update with your credentials)
connection_string = "postgresql://username:password@localhost:5432/wuzzuf"
engine = create_engine(connection_string)

# Test connection
test_query = "SELECT COUNT(*) FROM jobs"
result = pd.read_sql(test_query, engine)
print(f"Total jobs: {result.iloc[0, 0]:,}")
```

### Method 3: Using psql Command Line

```bash
# Connect to database
psql -h localhost -U username -d wuzzuf

# Test connection
\dt  -- List all tables
SELECT COUNT(*) FROM jobs;  -- Verify data
```

## Query Execution Instructions

### Using Python (Recommended)

```python
import pandas as pd

# Execute any query from queries.sql
query = """
SELECT 
    job_title,
    COUNT(*) as posting_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) as percentage
FROM jobs 
WHERE job_title IS NOT NULL 
    AND job_title != ''
GROUP BY job_title 
ORDER BY posting_count DESC 
LIMIT 10;
"""

result_df = pd.read_sql(query, engine)
print(result_df)
```

### Using SQL Client

1. Open your preferred SQL client (pgAdmin, DBeaver, etc.)
2. Connect to the `wuzzuf` database
3. Copy queries from `sql/queries.sql`
4. Execute queries individually or in batches

### Using Jupyter Notebook

Execute the provided `notebooks/03_sql_queries.ipynb` notebook which contains all queries with explanations and visualizations.

## Business Questions and Queries

### 1. Top Roles and Industries
**Business Question:** What are the most common job titles and hiring industries?

#### Query 1.1: Top 10 Job Titles
```sql
SELECT 
    job_title,
    COUNT(*) as posting_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) as percentage
FROM jobs 
WHERE job_title IS NOT NULL 
    AND job_title != ''
GROUP BY job_title 
ORDER BY posting_count DESC 
LIMIT 10;
```

**Expected Results:**
- Software Engineer: ~8,112 postings (32.30%)
- Data Engineer: ~3,462 postings (13.79%)
- Business Analyst: ~2,009 postings (8.00%)

**Business Context:** Identifies high-demand roles for recruitment strategy and career guidance.

#### Query 1.2: Top 10 Industries
```sql
SELECT 
    c.industry,
    COUNT(j.job_id) as posting_count,
    ROUND(COUNT(j.job_id) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) as percentage
FROM jobs j
JOIN companies c ON j.company_id = c.company_id
WHERE c.industry IS NOT NULL 
    AND c.industry != ''
GROUP BY c.industry 
ORDER BY posting_count DESC 
LIMIT 10;
```

**Expected Results:**
- Internet: ~5,055 postings (20.13%)
- Computer Software: ~4,720 postings (18.79%)
- Information Technology & Services: ~4,459 postings (17.76%)

**Business Context:** Shows industry hiring trends for market analysis and business development.

### 2. Skills Demand Analysis
**Business Question:** What are the top technical and soft skills in demand?

#### Query 2.1: Top 15 Skills Overall
```sql
SELECT 
    s.skill_name,
    s.skill_category,
    COUNT(js.job_id) as job_count,
    ROUND(COUNT(js.job_id) * 100.0 / (SELECT COUNT(DISTINCT job_id) FROM job_skills), 2) as percentage_of_jobs
FROM skills s
JOIN job_skills js ON s.skill_id = js.skill_id
WHERE s.skill_name IS NOT NULL 
    AND s.skill_name != ''
GROUP BY s.skill_name, s.skill_category
ORDER BY job_count DESC
LIMIT 15;
```

**Expected Results:**
- Cloud (technical): ~8,549 jobs (37.33%)
- SQL (technical): ~8,412 jobs (36.73%)
- Python (technical): ~7,986 jobs (34.87%)

**Business Context:** Guides skill development priorities and training program design.

### 3. Experience Requirements
**Business Question:** What is the distribution of experience level requirements?

#### Query 3.1: Experience Level Distribution
```sql
SELECT 
    experience_level,
    COUNT(*) as posting_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs WHERE experience_level IS NOT NULL), 2) as percentage
FROM jobs 
WHERE experience_level IS NOT NULL 
    AND experience_level != ''
GROUP BY experience_level 
ORDER BY posting_count DESC;
```

**Expected Results:**
- Mid (3-5 years): ~12,884 postings (51.30%)
- Senior (6+ years): ~7,005 postings (27.89%)
- Entry (0-2 years): ~5,225 postings (20.81%)

**Business Context:** Informs workforce planning and career progression strategies.

### 4. Salary Insights
**Business Question:** What are the salary trends and compensation patterns?

#### Query 4.1: Salary Data Coverage
```sql
SELECT 
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN salary_min IS NOT NULL AND salary_max IS NOT NULL THEN 1 END) as jobs_with_salary,
    ROUND(
        COUNT(CASE WHEN salary_min IS NOT NULL AND salary_max IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) as salary_coverage_percentage
FROM jobs;
```

**Expected Results:**
- Total Jobs: 25,114
- Jobs with Salary: 1,496
- Coverage: 5.96%

**Business Context:** Shows salary transparency levels and data availability for compensation analysis.

#### Query 4.2: Top Paying Roles
```sql
SELECT 
    job_title,
    COUNT(*) as job_count,
    ROUND(AVG(salary_min), 0) as avg_min_salary,
    ROUND(AVG(salary_max), 0) as avg_max_salary,
    ROUND(AVG((salary_min + salary_max) / 2.0), 0) as avg_mid_salary,
    ROUND(AVG(salary_max - salary_min), 0) as avg_salary_range
FROM jobs 
WHERE salary_min IS NOT NULL 
    AND salary_max IS NOT NULL
    AND job_title IS NOT NULL 
    AND job_title != ''
GROUP BY job_title 
HAVING COUNT(*) >= 10
ORDER BY avg_mid_salary DESC
LIMIT 10;
```

**Expected Results:**
- Machine Learning Engineer: ~$170,212 average
- Data Scientist: ~$147,650 average
- Product Manager: ~$136,597 average

**Business Context:** Enables competitive salary benchmarking and compensation planning.

### 5. Location Trends
**Business Question:** What are the geographic trends and location patterns?

#### Query 5.1: Top Cities
```sql
SELECT 
    city,
    COUNT(*) as job_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs WHERE city IS NOT NULL AND city != ''), 2) as percentage_of_city_jobs,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) as percentage_of_total_jobs
FROM jobs 
WHERE city IS NOT NULL 
    AND city != ''
    AND city != 'Unknown'
GROUP BY city 
ORDER BY job_count DESC
LIMIT 10;
```

**Expected Results:**
- New York: ~986 jobs (3.93%)
- San Francisco: ~848 jobs (3.38%)
- Chicago: ~622 jobs (2.48%)

**Business Context:** Identifies key markets for expansion and talent acquisition strategies.

### 6. Time Trends
**Business Question:** What are the temporal patterns and seasonal hiring trends?

#### Query 6.1: Peak Hiring Periods
```sql
SELECT 
    posting_year,
    posting_month,
    COUNT(*) as posting_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM jobs 
WHERE posting_year IS NOT NULL 
    AND posting_month IS NOT NULL
GROUP BY posting_year, posting_month
ORDER BY posting_count DESC
LIMIT 10;
```

**Expected Results:**
- 2020-06: 963 postings (3.83%)
- 2021-03: 945 postings (3.76%)
- 2021-02: 933 postings (3.72%)

**Business Context:** Optimizes recruitment timing and resource allocation.

## Query Validation

### Validation Checklist

Before executing queries, verify:

1. **Database Connection**
   ```sql
   SELECT current_database(), current_user, version();
   ```

2. **Table Existence and Row Counts**
   ```sql
   SELECT 'jobs' as table_name, COUNT(*) as row_count FROM jobs
   UNION ALL
   SELECT 'companies' as table_name, COUNT(*) as row_count FROM companies
   UNION ALL
   SELECT 'skills' as table_name, COUNT(*) as row_count FROM skills
   UNION ALL
   SELECT 'job_skills' as table_name, COUNT(*) as row_count FROM job_skills;
   ```

3. **Data Quality Check**
   ```sql
   -- Check for NULL values in key fields
   SELECT 
       COUNT(*) as total_jobs,
       COUNT(job_title) as jobs_with_title,
       COUNT(experience_level) as jobs_with_experience,
       COUNT(salary_min) as jobs_with_salary
   FROM jobs;
   ```

### Expected Validation Results

| Table | Expected Row Count |
|-------|-------------------|
| jobs | 25,114 |
| companies | 4,468 |
| skills | 167 |
| job_skills | 159,894 |

## Expected Results

### Summary of Key Findings

1. **Market Concentration**
   - Top 5 job titles account for ~67% of all postings
   - Technology sector dominates with ~56% market share
   - Geographic concentration in major US metropolitan areas

2. **Skills Landscape**
   - Technical skills heavily outweigh soft skills in demand
   - Cloud computing and data skills are most sought after
   - Programming languages (Python, Java, JavaScript) show strong demand

3. **Experience Distribution**
   - Mid-level positions offer the most opportunities
   - Clear career progression path from Entry → Mid → Senior
   - Senior roles command premium compensation

4. **Compensation Insights**
   - Limited salary transparency (only 5.96% of jobs)
   - Machine Learning and Data Science roles offer highest pay
   - Clear salary progression with experience level

5. **Geographic Patterns**
   - US market dominance with 94% of postings
   - New York and San Francisco lead city rankings
   - Technology hubs concentrate job opportunities

6. **Temporal Trends**
   - Peak hiring in summer months (June-July)
   - 2020-2021 period shows highest activity
   - Seasonal patterns suggest strategic hiring windows

## Troubleshooting

### Common Issues and Solutions

#### Connection Issues
```
Error: could not connect to server
```
**Solution:** Verify PostgreSQL is running and connection parameters are correct.

#### Permission Errors
```
Error: permission denied for table jobs
```
**Solution:** Ensure database user has SELECT permissions on all tables.

#### Memory Issues with Large Results
```
Error: out of memory
```
**Solution:** Add LIMIT clauses to queries or process results in chunks.

#### Slow Query Performance
**Solution:** Ensure proper indexes exist:
```sql
-- Check existing indexes
SELECT tablename, indexname, indexdef 
FROM pg_indexes 
WHERE tablename IN ('jobs', 'companies', 'skills', 'job_skills');

-- Create indexes if needed
CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(job_title);
CREATE INDEX IF NOT EXISTS idx_jobs_experience ON jobs(experience_level);
CREATE INDEX IF NOT EXISTS idx_jobs_salary ON jobs(salary_min, salary_max);
```

## Performance Optimization

### Query Optimization Tips

1. **Use Appropriate Filters**
   - Always filter out NULL and empty values
   - Use specific date ranges when analyzing time trends
   - Limit result sets with TOP/LIMIT clauses

2. **Index Usage**
   - Ensure indexes exist on frequently queried columns
   - Use EXPLAIN ANALYZE to check query execution plans

3. **Join Optimization**
   - Use appropriate join types (INNER vs LEFT JOIN)
   - Ensure join conditions use indexed columns

4. **Aggregation Efficiency**
   - Use window functions for complex calculations
   - Consider materialized views for frequently accessed aggregations

### Sample Optimized Query
```sql
-- Optimized version with proper indexing and filtering
SELECT 
    job_title,
    COUNT(*) as posting_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM jobs 
WHERE job_title IS NOT NULL 
    AND job_title != ''
    AND posting_date >= '2017-01-01'  -- Specific date range
GROUP BY job_title 
HAVING COUNT(*) >= 10  -- Filter small groups
ORDER BY posting_count DESC 
LIMIT 10;
```

## Conclusion

This guide provides comprehensive instructions for executing and understanding the SQL queries in the Wuzzuf Job Market Analysis project. All queries are validated against the EDA analysis results and provide actionable business intelligence insights.

For additional support or questions about query execution, refer to the `notebooks/03_sql_queries.ipynb` notebook which demonstrates all queries with expected outputs and business context.

---

**Last Updated:** 2024  
**Version:** 1.0  
**Contact:** Data Analysis Team