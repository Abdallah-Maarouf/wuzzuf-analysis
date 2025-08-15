-- =====================================================
-- WUZZUF JOB MARKET ANALYSIS - COMPREHENSIVE SQL QUERIES
-- =====================================================
-- This file contains all SQL queries used for the 6 key business questions
-- in the Wuzzuf Job Market Analysis project.
--
-- Each query is documented with:
-- - Business question it answers
-- - Expected output format
-- - Business context and insights
--
-- Author: Data Analysis Team
-- Date: 2024
-- =====================================================

-- =====================================================
-- BUSINESS QUESTION 1: TOP ROLES AND INDUSTRIES
-- What are the most common job titles and hiring industries?
-- =====================================================

-- Query 1.1: Top 10 Job Titles by Posting Count
-- Purpose: Identify the most in-demand job roles in the market
-- Expected Output: Job title, posting count, percentage of total market
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

-- Query 1.2: Top 10 Industries by Posting Volume
-- Purpose: Identify which industries are hiring most actively
-- Expected Output: Industry, posting count, percentage of total market
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

-- =====================================================
-- BUSINESS QUESTION 2: SKILLS DEMAND ANALYSIS
-- What are the top technical and soft skills in demand?
-- =====================================================

-- Query 2.1: Top 15 Skills Overall (Technical & Soft)
-- Purpose: Identify the most demanded skills across all job postings
-- Expected Output: Skill name, category, job count, percentage of jobs requiring skill
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

-- Query 2.2: Top 10 Technical Skills
-- Purpose: Focus specifically on technical skills demand
-- Expected Output: Technical skill name, job count, percentage of jobs
SELECT 
    s.skill_name,
    COUNT(js.job_id) as job_count,
    ROUND(COUNT(js.job_id) * 100.0 / (SELECT COUNT(DISTINCT job_id) FROM job_skills), 2) as percentage_of_jobs
FROM skills s
JOIN job_skills js ON s.skill_id = js.skill_id
WHERE s.skill_category = 'technical'
    AND s.skill_name IS NOT NULL 
    AND s.skill_name != ''
GROUP BY s.skill_name
ORDER BY job_count DESC
LIMIT 10;

-- =====================================================
-- BUSINESS QUESTION 3: EXPERIENCE REQUIREMENTS
-- What is the distribution of experience level requirements?
-- =====================================================

-- Query 3.1: Experience Level Distribution with Percentages
-- Purpose: Show overall distribution of job postings across experience levels
-- Expected Output: Experience level, posting count, percentage of total
SELECT 
    experience_level,
    COUNT(*) as posting_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs WHERE experience_level IS NOT NULL), 2) as percentage
FROM jobs 
WHERE experience_level IS NOT NULL 
    AND experience_level != ''
GROUP BY experience_level 
ORDER BY posting_count DESC;

-- Query 3.2: Experience Distribution by Top Job Roles
-- Purpose: Examine experience requirements for the most common job titles
-- Expected Output: Job title, experience level, posting count, percentage within role
WITH top_roles AS (
    SELECT job_title
    FROM jobs 
    WHERE job_title IS NOT NULL AND job_title != ''
    GROUP BY job_title
    ORDER BY COUNT(*) DESC
    LIMIT 5
)
SELECT 
    j.job_title,
    j.experience_level,
    COUNT(*) as posting_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY j.job_title), 2) as percentage_within_role
FROM jobs j
JOIN top_roles tr ON j.job_title = tr.job_title
WHERE j.experience_level IS NOT NULL 
    AND j.experience_level != ''
GROUP BY j.job_title, j.experience_level
ORDER BY j.job_title, posting_count DESC;

-- =====================================================
-- BUSINESS QUESTION 4: SALARY INSIGHTS
-- What are the salary trends and compensation patterns?
-- =====================================================

-- Query 4.1: Data Coverage Analysis
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

-- Query 4.2: Average Salaries by Job Role
-- Purpose: Identify highest paying job roles with statistical analysis
-- Expected Output: Job title, job count, avg min/max/mid salary, salary range
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

-- Query 4.3: Average Salaries by Experience Level
-- Purpose: Analyze compensation progression across experience levels
-- Expected Output: Experience level, job count, salary statistics
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

-- =====================================================
-- BUSINESS QUESTION 5: LOCATION TRENDS
-- What are the geographic trends and location patterns?
-- =====================================================

-- Query 5.1: Location Data Quality Analysis
-- Purpose: Assess the completeness and quality of location data
-- Expected Output: Coverage statistics for city and country fields
SELECT 
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN city IS NOT NULL AND city != '' THEN 1 END) as jobs_with_city,
    COUNT(CASE WHEN country IS NOT NULL AND country != '' THEN 1 END) as jobs_with_country,
    ROUND(
        COUNT(CASE WHEN city IS NOT NULL AND city != '' THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) as city_coverage_percentage,
    ROUND(
        COUNT(CASE WHEN country IS NOT NULL AND country != '' THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) as country_coverage_percentage
FROM jobs;

-- Query 5.2: Top 10 Cities by Job Posting Volume
-- Purpose: Identify cities with the highest concentration of job postings
-- Expected Output: City, job count, percentage of city jobs, percentage of total jobs
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

-- Query 5.3: Top 10 Countries by Job Posting Volume
-- Purpose: Analyze job posting distribution across different countries
-- Expected Output: Country, job count, percentage of country jobs, percentage of total jobs
SELECT 
    country,
    COUNT(*) as job_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs WHERE country IS NOT NULL AND country != ''), 2) as percentage_of_country_jobs,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) as percentage_of_total_jobs
FROM jobs 
WHERE country IS NOT NULL 
    AND country != ''
    AND country != 'Unknown'
GROUP BY country 
ORDER BY job_count DESC
LIMIT 10;

-- =====================================================
-- BUSINESS QUESTION 6: TIME TRENDS
-- What are the temporal patterns and seasonal hiring trends?
-- =====================================================

-- Query 6.1: Data Overview - Time Range Analysis
-- Purpose: Understand the temporal scope of the dataset
-- Expected Output: Date range, total jobs, unique years/months, average monthly postings
SELECT 
    MIN(posting_date) as earliest_date,
    MAX(posting_date) as latest_date,
    COUNT(*) as total_jobs,
    COUNT(DISTINCT posting_year) as unique_years,
    COUNT(DISTINCT posting_month) as unique_months,
    ROUND(COUNT(*)::numeric / COUNT(DISTINCT posting_year * 12 + posting_month), 0) as avg_jobs_per_month
FROM jobs 
WHERE posting_date IS NOT NULL;

-- Query 6.2: Top 10 Months by Posting Volume
-- Purpose: Identify peak hiring periods by month and year
-- Expected Output: Year, month, month name, posting count, percentage, rank
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

-- Query 6.3: Seasonal Analysis
-- Purpose: Analyze hiring patterns by season to identify seasonal trends
-- Expected Output: Month, season, total postings, percentage, performance indicator
WITH seasonal_data AS (
    SELECT 
        posting_month,
        COUNT(*) as total_postings,
        CASE 
            WHEN posting_month IN (12, 1, 2) THEN 'Winter'
            WHEN posting_month IN (3, 4, 5) THEN 'Spring'
            WHEN posting_month IN (6, 7, 8) THEN 'Summer'
            WHEN posting_month IN (9, 10, 11) THEN 'Fall'
        END as season,
        CASE posting_month
            WHEN 1 THEN 'January'
            WHEN 2 THEN 'February'
            WHEN 3 THEN 'March'
            WHEN 4 THEN 'April'
            WHEN 5 THEN 'May'
            WHEN 6 THEN 'June'
            WHEN 7 THEN 'July'
            WHEN 8 THEN 'August'
            WHEN 9 THEN 'September'
            WHEN 10 THEN 'October'
            WHEN 11 THEN 'November'
            WHEN 12 THEN 'December'
        END as month_name
    FROM jobs 
    WHERE posting_month IS NOT NULL
    GROUP BY posting_month
)
SELECT 
    posting_month,
    month_name,
    season,
    total_postings,
    ROUND(total_postings * 100.0 / SUM(total_postings) OVER(), 2) as percentage,
    CASE 
        WHEN total_postings > AVG(total_postings) OVER() THEN 'Above Average'
        WHEN total_postings < AVG(total_postings) OVER() THEN 'Below Average'
        ELSE 'Average'
    END as performance
FROM seasonal_data
ORDER BY posting_month;

-- =====================================================
-- VALIDATION QUERIES
-- =====================================================
-- These queries help validate that the analysis results match the EDA outputs

-- Validation Query V.1: Database Overview
-- Purpose: Verify table row counts match EDA analysis
SELECT 'jobs' as table_name, COUNT(*) as row_count FROM jobs
UNION ALL
SELECT 'companies' as table_name, COUNT(*) as row_count FROM companies
UNION ALL
SELECT 'skills' as table_name, COUNT(*) as row_count FROM skills
UNION ALL
SELECT 'job_skills' as table_name, COUNT(*) as row_count FROM job_skills
ORDER BY table_name;

-- Validation Query V.2: Skills Data Coverage
-- Purpose: Verify skills analysis coverage matches EDA results
SELECT 
    COUNT(DISTINCT s.skill_id) as total_skills,
    COUNT(DISTINCT js.job_id) as jobs_with_skills,
    COUNT(*) as total_skill_mentions
FROM skills s
JOIN job_skills js ON s.skill_id = js.skill_id;

-- =====================================================
-- BUSINESS INSIGHTS SUMMARY
-- =====================================================
-- Key findings from the analysis:
--
-- 1. TOP ROLES & INDUSTRIES:
--    - Software Engineer dominates with ~32% of job postings
--    - Technology sector (Internet, Computer Software, IT Services) leads hiring
--    - High market concentration in top roles and industries
--
-- 2. SKILLS DEMAND:
--    - Cloud, SQL, and Python are the most demanded technical skills
--    - Strong emphasis on programming and data-related skills
--    - Technical skills significantly outweigh soft skills in demand
--
-- 3. EXPERIENCE REQUIREMENTS:
--    - Mid-level positions (3-5 years) represent ~51% of opportunities
--    - Senior roles account for ~28% of postings
--    - Entry-level positions make up ~21% of the market
--
-- 4. SALARY INSIGHTS:
--    - Only ~6% of job postings include salary information
--    - Machine Learning Engineers command highest average salaries
--    - Clear salary progression from Entry to Senior levels
--
-- 5. LOCATION TRENDS:
--    - New York and San Francisco lead in job posting volume
--    - United States dominates the geographic distribution
--    - Strong concentration in major metropolitan areas
--
-- 6. TIME TRENDS:
--    - Peak hiring activity in mid-2020 and early 2021
--    - Summer months show higher posting volumes
--    - Clear seasonal patterns in hiring activity
--
-- =====================================================
-- END OF COMPREHENSIVE SQL QUERIES
-- =====================================================