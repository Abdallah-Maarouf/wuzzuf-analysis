-- Wuzzuf Job Market Analysis - SQL Queries
-- This file contains all SQL queries used for business intelligence analysis
-- Each query corresponds to one of the 6 key business questions

-- =============================================================================
-- Analysis 1: Top Roles and Industries
-- Business Question: What are the most common job titles and hiring industries?
-- =============================================================================

-- Query 1.1: Top 10 Job Titles by Posting Count
-- This query identifies the most in-demand job roles in the market
-- Results show job title, number of postings, and percentage of total market
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
-- This query identifies which industries are hiring most actively
-- Results show industry, number of job postings, and market share percentage
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

-- Query 1.3: Combined Top Roles and Industries Summary
-- This query provides a comprehensive view of market concentration
-- Shows total jobs, unique titles, unique industries, and concentration metrics
SELECT 
    'Market Overview' as metric_type,
    (SELECT COUNT(*) FROM jobs) as total_jobs,
    (SELECT COUNT(DISTINCT job_title) FROM jobs WHERE job_title IS NOT NULL AND job_title != '') as unique_job_titles,
    (SELECT COUNT(DISTINCT c.industry) FROM jobs j JOIN companies c ON j.company_id = c.company_id WHERE c.industry IS NOT NULL AND c.industry != '') as unique_industries,
    (SELECT ROUND(SUM(percentage), 2) FROM (
        SELECT ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) as percentage
        FROM jobs 
        WHERE job_title IS NOT NULL AND job_title != ''
        GROUP BY job_title 
        ORDER BY COUNT(*) DESC 
        LIMIT 5
    ) top5_roles) as top5_roles_market_share,
    (SELECT ROUND(SUM(percentage), 2) FROM (
        SELECT ROUND(COUNT(j.job_id) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) as percentage
        FROM jobs j
        JOIN companies c ON j.company_id = c.company_id
        WHERE c.industry IS NOT NULL AND c.industry != ''
        GROUP BY c.industry 
        ORDER BY COUNT(j.job_id) DESC 
        LIMIT 5
    ) top5_industries) as top5_industries_market_share;

-- =============================================================================
-- Expected Results Summary for Analysis 1:
-- 
-- Query 1.1 should return:
-- - Top job title: Software Engineer (~32% of market)
-- - Strong demand for technical roles (Software Engineer, Data Engineer, etc.)
-- - High market concentration in top roles
--
-- Query 1.2 should return:
-- - Top industry: Internet/Technology sector (~20% of market)  
-- - Technology and IT services dominate hiring
-- - Significant presence of staffing & recruiting industry
--
-- Query 1.3 should return:
-- - Total market size and diversity metrics
-- - Market concentration percentages for top 5 roles and industries
-- - Overall market structure insights
-- =============================================================================