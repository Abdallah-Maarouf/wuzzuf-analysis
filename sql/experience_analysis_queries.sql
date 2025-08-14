-- Experience Requirements Analysis Queries
-- This file contains SQL queries for analyzing experience level distribution in the Wuzzuf job market data
-- Business Question: What is the distribution of experience level requirements across job postings?

-- =============================================================================
-- Query 1: Overall Experience Level Distribution with Percentages
-- =============================================================================
-- This query shows the overall distribution of job postings across experience levels
-- with both absolute counts and percentages

SELECT 
    experience_level,
    COUNT(*) as posting_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs WHERE experience_level IS NOT NULL), 2) as percentage
FROM jobs 
WHERE experience_level IS NOT NULL 
    AND experience_level != ''
GROUP BY experience_level 
ORDER BY posting_count DESC;

-- =============================================================================
-- Query 2: Experience Distribution by Industry
-- =============================================================================
-- This query analyzes how experience requirements vary across different industries
-- Shows the percentage distribution within each industry

SELECT 
    c.industry,
    j.experience_level,
    COUNT(*) as posting_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY c.industry), 2) as percentage_within_industry
FROM jobs j
JOIN companies c ON j.company_id = c.company_id
WHERE j.experience_level IS NOT NULL 
    AND j.experience_level != ''
    AND c.industry IS NOT NULL 
    AND c.industry != ''
GROUP BY c.industry, j.experience_level
ORDER BY c.industry, posting_count DESC
LIMIT 30;

-- =============================================================================
-- Query 3: Experience Distribution by Top Job Roles
-- =============================================================================
-- This query examines experience requirements for the top 5 most common job titles
-- Shows how experience distribution varies by role

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

-- =============================================================================
-- Query 4: Experience Level Summary Statistics
-- =============================================================================
-- This query provides summary statistics for experience level analysis

SELECT 
    'Total Jobs with Experience Data' as metric,
    COUNT(*)::text as value
FROM jobs 
WHERE experience_level IS NOT NULL AND experience_level != ''

UNION ALL

SELECT 
    'Most Common Experience Level' as metric,
    experience_level as value
FROM (
    SELECT 
        experience_level,
        COUNT(*) as cnt,
        ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) as rn
    FROM jobs 
    WHERE experience_level IS NOT NULL AND experience_level != ''
    GROUP BY experience_level
) ranked
WHERE rn = 1

UNION ALL

SELECT 
    'Number of Distinct Experience Levels' as metric,
    COUNT(DISTINCT experience_level)::text as value
FROM jobs 
WHERE experience_level IS NOT NULL AND experience_level != '';

-- =============================================================================
-- Query 5: Cross-tabulation of Experience by Industry (Top 10 Industries)
-- =============================================================================
-- This query creates a cross-tabulation view showing experience distribution
-- across the top 10 industries by job posting volume

WITH top_industries AS (
    SELECT c.industry
    FROM jobs j
    JOIN companies c ON j.company_id = c.company_id
    WHERE c.industry IS NOT NULL AND c.industry != ''
    GROUP BY c.industry
    ORDER BY COUNT(*) DESC
    LIMIT 10
),
experience_crosstab AS (
    SELECT 
        c.industry,
        SUM(CASE WHEN j.experience_level = 'Entry' THEN 1 ELSE 0 END) as entry_count,
        SUM(CASE WHEN j.experience_level = 'Mid' THEN 1 ELSE 0 END) as mid_count,
        SUM(CASE WHEN j.experience_level = 'Senior' THEN 1 ELSE 0 END) as senior_count,
        COUNT(*) as total_count
    FROM jobs j
    JOIN companies c ON j.company_id = c.company_id
    JOIN top_industries ti ON c.industry = ti.industry
    WHERE j.experience_level IS NOT NULL AND j.experience_level != ''
    GROUP BY c.industry
)
SELECT 
    industry,
    entry_count,
    ROUND(entry_count * 100.0 / total_count, 1) as entry_percentage,
    mid_count,
    ROUND(mid_count * 100.0 / total_count, 1) as mid_percentage,
    senior_count,
    ROUND(senior_count * 100.0 / total_count, 1) as senior_percentage,
    total_count
FROM experience_crosstab
ORDER BY total_count DESC;

-- =============================================================================
-- Query 6: Experience Requirements Trend Analysis
-- =============================================================================
-- This query analyzes experience requirements over time (by posting month/year)

SELECT 
    posting_year,
    posting_month,
    experience_level,
    COUNT(*) as posting_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY posting_year, posting_month), 2) as percentage_within_month
FROM jobs 
WHERE experience_level IS NOT NULL 
    AND experience_level != ''
    AND posting_year IS NOT NULL
    AND posting_month IS NOT NULL
GROUP BY posting_year, posting_month, experience_level
ORDER BY posting_year DESC, posting_month DESC, posting_count DESC;