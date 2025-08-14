-- =====================================================
-- Wuzzuf Job Market Analysis - EDA SQL Queries
-- =====================================================
-- This file contains all SQL queries used in the EDA analysis
-- for roles/industries and skills demand analysis

-- =====================================================
-- ANALYSIS 1: TOP ROLES AND INDUSTRIES
-- =====================================================

-- Query 1.1: Top 10 Job Titles by Posting Count
-- Business Question: What are the most common job titles?
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
-- Business Question: Which industries are hiring the most?
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
-- ANALYSIS 2: SKILLS DEMAND ANALYSIS
-- =====================================================

-- Query 2.1: Skills Data Overview
-- Get overall statistics about skills data
SELECT 
    COUNT(DISTINCT s.skill_id) as total_skills,
    COUNT(DISTINCT js.job_id) as jobs_with_skills,
    COUNT(*) as total_skill_mentions
FROM skills s
JOIN job_skills js ON s.skill_id = js.skill_id;
-- Query 
2.2: Top 15 Skills Overall (Technical & Soft)
-- Business Question: What are the most demanded skills overall?
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

-- Query 2.3: Top 10 Technical Skills
-- Business Question: What are the most demanded technical skills?
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

-- Query 2.4: Top 10 Soft Skills
-- Business Question: What are the most demanded soft skills?
SELECT 
    s.skill_name,
    COUNT(js.job_id) as job_count,
    ROUND(COUNT(js.job_id) * 100.0 / (SELECT COUNT(DISTINCT job_id) FROM job_skills), 2) as percentage_of_jobs
FROM skills s
JOIN job_skills js ON s.skill_id = js.skill_id
WHERE s.skill_category = 'soft'
    AND s.skill_name IS NOT NULL 
    AND s.skill_name != ''
GROUP BY s.skill_name
ORDER BY job_count DESC
LIMIT 10;-- Quer
y 2.5: Skills by Role Analysis
-- Business Question: What skills are most demanded for each top job role?
SELECT 
    j.job_title,
    s.skill_name,
    s.skill_category,
    COUNT(*) as mention_count
FROM jobs j
JOIN job_skills js ON j.job_id = js.job_id
JOIN skills s ON js.skill_id = s.skill_id
WHERE j.job_title IN (
    SELECT job_title 
    FROM jobs 
    WHERE job_title IS NOT NULL AND job_title != ''
    GROUP BY job_title 
    ORDER BY COUNT(*) DESC 
    LIMIT 5
)
    AND s.skill_name IS NOT NULL 
    AND s.skill_name != ''
GROUP BY j.job_title, s.skill_name, s.skill_category
ORDER BY j.job_title, mention_count DESC;

-- Query 2.6: Skills by Industry Analysis
-- Business Question: What skills are most demanded in each top industry?
SELECT 
    c.industry,
    s.skill_name,
    s.skill_category,
    COUNT(*) as mention_count
FROM jobs j
JOIN companies c ON j.company_id = c.company_id
JOIN job_skills js ON j.job_id = js.job_id
JOIN skills s ON js.skill_id = s.skill_id
WHERE c.industry IN (
    SELECT c2.industry 
    FROM jobs j2
    JOIN companies c2 ON j2.company_id = c2.company_id
    WHERE c2.industry IS NOT NULL AND c2.industry != ''
    GROUP BY c2.industry 
    ORDER BY COUNT(j2.job_id) DESC 
    LIMIT 3
)
    AND s.skill_name IS NOT NULL 
    AND s.skill_name != ''
GROUP BY c.industry, s.skill_name, s.skill_category
ORDER BY c.industry, mention_count DESC;-- ====
=================================================
-- UTILITY QUERIES
-- =====================================================

-- Query U.1: Database Overview - Table Row Counts
-- Get row counts for all main tables
SELECT 'jobs' as table_name, COUNT(*) as row_count FROM jobs
UNION ALL
SELECT 'companies' as table_name, COUNT(*) as row_count FROM companies
UNION ALL
SELECT 'skills' as table_name, COUNT(*) as row_count FROM skills
UNION ALL
SELECT 'job_skills' as table_name, COUNT(*) as row_count FROM job_skills
ORDER BY table_name;

-- Query U.2: Skills Category Distribution
-- Get distribution of skills by category
SELECT 
    skill_category,
    COUNT(*) as skill_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM skills), 2) as percentage
FROM skills
WHERE skill_category IS NOT NULL
GROUP BY skill_category
ORDER BY skill_count DESC;

-- Query U.3: Jobs with Skills Coverage
-- Check what percentage of jobs have skills data
SELECT 
    'Total Jobs' as metric,
    COUNT(*) as count
FROM jobs
UNION ALL
SELECT 
    'Jobs with Skills' as metric,
    COUNT(DISTINCT job_id) as count
FROM job_skills
UNION ALL
SELECT 
    'Coverage Percentage' as metric,
    ROUND(
        (SELECT COUNT(DISTINCT job_id) FROM job_skills) * 100.0 / 
        (SELECT COUNT(*) FROM jobs), 2
    ) as count;

-- =====================================================
-- END OF QUERIES
-- =====================================================