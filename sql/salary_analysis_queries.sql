-- =====================================================
-- Wuzzuf Job Market Analysis - Salary Insights Queries
-- =====================================================
-- Business Question: What are the salary trends and compensation patterns 
-- across different roles, industries, and experience levels?
--
-- This file contains SQL queries for analyzing salary data coverage,
-- compensation by role, industry, and experience level, plus statistical summaries.
-- =====================================================

-- Query 1: Data Coverage Analysis
-- Purpose: Determine what percentage of job postings include salary information
-- Expected Output: Total jobs, jobs with salary data, coverage percentage
SELECT 
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN salary_min IS NOT NULL AND salary_max IS NOT NULL THEN 1 END) as jobs_with_salary,
    ROUND(
        COUNT(CASE WHEN salary_min IS NOT NULL AND salary_max IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) as salary_coverage_percentage
FROM jobs;

-- Query 2: Average Salaries by Job Role
-- Purpose: Identify highest paying job roles with statistical analysis
-- Expected Output: Top 10 roles by average mid-point salary with job counts and ranges
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
HAVING COUNT(*) >= 10  -- Only roles with at least 10 salary data points
ORDER BY avg_mid_salary DESC
LIMIT 10;

-- Query 3: Average Salaries by Industry
-- Purpose: Compare compensation patterns across different industries
-- Expected Output: Top 10 industries by average mid-point salary with statistical summaries
SELECT 
    c.industry,
    COUNT(*) as job_count,
    ROUND(AVG(j.salary_min), 0) as avg_min_salary,
    ROUND(AVG(j.salary_max), 0) as avg_max_salary,
    ROUND(AVG((j.salary_min + j.salary_max) / 2.0), 0) as avg_mid_salary,
    ROUND(AVG(j.salary_max - j.salary_min), 0) as avg_salary_range
FROM jobs j
JOIN companies c ON j.company_id = c.company_id
WHERE j.salary_min IS NOT NULL 
    AND j.salary_max IS NOT NULL
    AND c.industry IS NOT NULL 
    AND c.industry != ''
GROUP BY c.industry 
HAVING COUNT(*) >= 5  -- Only industries with at least 5 salary data points
ORDER BY avg_mid_salary DESC
LIMIT 10;

-- Query 4: Average Salaries by Experience Level
-- Purpose: Analyze compensation progression across experience levels
-- Expected Output: Salary statistics for Entry, Mid, and Senior levels
SELECT 
    experience_level,
    COUNT(*) as job_count,
    ROUND(AVG(salary_min), 0) as avg_min_salary,
    ROUND(AVG(salary_max), 0) as avg_max_salary,
    ROUND(AVG((salary_min + salary_max) / 2.0), 0) as avg_mid_salary,
    ROUND(AVG(salary_max - salary_min), 0) as avg_salary_range
FROM jobs 
WHERE salary_min IS NOT NULL 
    AND salary_max IS NOT NULL
    AND experience_level IS NOT NULL 
    AND experience_level != ''
GROUP BY experience_level 
ORDER BY 
    CASE experience_level 
        WHEN 'Entry' THEN 1 
        WHEN 'Mid' THEN 2 
        WHEN 'Senior' THEN 3 
        ELSE 4 
    END;

-- Query 5: Salary Distribution Statistics
-- Purpose: Provide overall salary market statistics and percentiles
-- Expected Output: Min, max, median, and percentile salary distributions
SELECT 
    COUNT(*) as total_salary_records,
    ROUND(MIN(salary_min), 0) as min_salary_floor,
    ROUND(MAX(salary_max), 0) as max_salary_ceiling,
    ROUND(AVG(salary_min), 0) as avg_min_salary,
    ROUND(AVG(salary_max), 0) as avg_max_salary,
    ROUND(AVG((salary_min + salary_max) / 2.0), 0) as overall_avg_salary,
    ROUND(STDDEV((salary_min + salary_max) / 2.0), 0) as salary_std_deviation
FROM jobs 
WHERE salary_min IS NOT NULL 
    AND salary_max IS NOT NULL;

-- Query 6: Top Paying Role-Industry Combinations
-- Purpose: Identify the highest paying role-industry combinations
-- Expected Output: Top 10 role-industry pairs by average salary
SELECT 
    j.job_title,
    c.industry,
    COUNT(*) as job_count,
    ROUND(AVG((j.salary_min + j.salary_max) / 2.0), 0) as avg_salary,
    ROUND(MIN((j.salary_min + j.salary_max) / 2.0), 0) as min_salary,
    ROUND(MAX((j.salary_min + j.salary_max) / 2.0), 0) as max_salary
FROM jobs j
JOIN companies c ON j.company_id = c.company_id
WHERE j.salary_min IS NOT NULL 
    AND j.salary_max IS NOT NULL
    AND j.job_title IS NOT NULL 
    AND j.job_title != ''
    AND c.industry IS NOT NULL 
    AND c.industry != ''
GROUP BY j.job_title, c.industry
HAVING COUNT(*) >= 3  -- At least 3 positions for statistical relevance
ORDER BY avg_salary DESC
LIMIT 10;

-- Query 7: Salary Analysis by Experience and Role
-- Purpose: Compare how experience affects salary within specific roles
-- Expected Output: Salary progression by experience level for top roles
WITH top_roles AS (
    SELECT job_title
    FROM jobs 
    WHERE salary_min IS NOT NULL AND salary_max IS NOT NULL
        AND job_title IS NOT NULL AND job_title != ''
    GROUP BY job_title
    ORDER BY COUNT(*) DESC
    LIMIT 5
)
SELECT 
    j.job_title,
    j.experience_level,
    COUNT(*) as job_count,
    ROUND(AVG((j.salary_min + j.salary_max) / 2.0), 0) as avg_salary,
    ROUND(MIN((j.salary_min + j.salary_max) / 2.0), 0) as min_salary,
    ROUND(MAX((j.salary_min + j.salary_max) / 2.0), 0) as max_salary
FROM jobs j
JOIN top_roles tr ON j.job_title = tr.job_title
WHERE j.salary_min IS NOT NULL 
    AND j.salary_max IS NOT NULL
    AND j.experience_level IS NOT NULL 
    AND j.experience_level != ''
GROUP BY j.job_title, j.experience_level
ORDER BY j.job_title, 
    CASE j.experience_level 
        WHEN 'Entry' THEN 1 
        WHEN 'Mid' THEN 2 
        WHEN 'Senior' THEN 3 
        ELSE 4 
    END;

-- =====================================================
-- Query Execution Notes:
-- =====================================================
-- 1. All queries filter for records with valid salary data (NOT NULL)
-- 2. Minimum job count thresholds ensure statistical relevance
-- 3. Results are ordered by average mid-point salary (salary_min + salary_max) / 2
-- 4. Salary ranges show the spread between minimum and maximum offered salaries
-- 5. Experience levels are ordered logically: Entry -> Mid -> Senior
-- 
-- Business Context:
-- These queries support analysis of salary transparency, compensation benchmarking,
-- and market rate analysis across roles, industries, and experience levels.
-- The results help identify high-value career paths and compensation trends.
-- =====================================================