-- =====================================================
-- Wuzzuf Job Market Analysis - Location Trends Queries
-- =====================================================
-- This file contains SQL queries for analyzing geographic distribution
-- and location trends in the Wuzzuf job market dataset.
--
-- Business Question: What are the geographic trends and location-based 
-- distribution patterns in job postings?
--
-- Author: Data Analysis Team
-- Date: 2024
-- =====================================================

-- =====================================================
-- 1. LOCATION DATA QUALITY ANALYSIS
-- =====================================================
-- Purpose: Assess the completeness and quality of location data
-- Expected Output: Coverage statistics for city and country fields

SELECT 
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN city IS NOT NULL AND city != '' THEN 1 END) as jobs_with_city,
    COUNT(CASE WHEN country IS NOT NULL AND country != '' THEN 1 END) as jobs_with_country,
    COUNT(CASE WHEN city IS NOT NULL AND city != '' AND country IS NOT NULL AND country != '' THEN 1 END) as jobs_with_both,
    ROUND(
        COUNT(CASE WHEN city IS NOT NULL AND city != '' THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) as city_coverage_percentage,
    ROUND(
        COUNT(CASE WHEN country IS NOT NULL AND country != '' THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) as country_coverage_percentage
FROM jobs;

-- =====================================================
-- 2. TOP CITIES BY JOB POSTING VOLUME
-- =====================================================
-- Purpose: Identify cities with the highest concentration of job postings
-- Expected Output: Top 10 cities ranked by job count with percentages

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

-- =====================================================
-- 3. TOP COUNTRIES BY JOB POSTING VOLUME
-- =====================================================
-- Purpose: Analyze job posting distribution across different countries
-- Expected Output: Top 10 countries ranked by job count with percentages

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
-- 4. CITY-COUNTRY BREAKDOWN ANALYSIS
-- =====================================================
-- Purpose: Analyze job distribution by city-country combinations
-- Expected Output: Top city-country pairs with job counts

SELECT 
    city,
    country,
    COUNT(*) as job_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs WHERE city IS NOT NULL AND country IS NOT NULL), 2) as percentage_of_located_jobs
FROM jobs 
WHERE city IS NOT NULL 
    AND city != ''
    AND city != 'Unknown'
    AND country IS NOT NULL 
    AND country != ''
    AND country != 'Unknown'
GROUP BY city, country 
ORDER BY job_count DESC
LIMIT 15;

-- =====================================================
-- 5. GEOGRAPHIC CONCENTRATION ANALYSIS
-- =====================================================
-- Purpose: Measure geographic concentration and market distribution
-- Expected Output: Concentration metrics for top locations

WITH city_stats AS (
    SELECT 
        city,
        COUNT(*) as job_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs WHERE city IS NOT NULL AND city != ''), 2) as city_percentage
    FROM jobs 
    WHERE city IS NOT NULL AND city != '' AND city != 'Unknown'
    GROUP BY city 
    ORDER BY job_count DESC
),
country_stats AS (
    SELECT 
        country,
        COUNT(*) as job_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs WHERE country IS NOT NULL AND country != ''), 2) as country_percentage
    FROM jobs 
    WHERE country IS NOT NULL AND country != '' AND country != 'Unknown'
    GROUP BY country 
    ORDER BY job_count DESC
)
SELECT 
    'Top 5 Cities' as metric,
    SUM(job_count) as total_jobs,
    ROUND(SUM(city_percentage), 2) as cumulative_percentage
FROM (SELECT * FROM city_stats LIMIT 5) top_cities
UNION ALL
SELECT 
    'Top 3 Countries' as metric,
    SUM(job_count) as total_jobs,
    ROUND(SUM(country_percentage), 2) as cumulative_percentage
FROM (SELECT * FROM country_stats LIMIT 3) top_countries;

-- =====================================================
-- 6. LOCATION TRENDS BY INDUSTRY
-- =====================================================
-- Purpose: Analyze how different industries are distributed geographically
-- Expected Output: Industry distribution across top cities

SELECT 
    j.city,
    c.industry,
    COUNT(*) as job_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY j.city), 2) as percentage_in_city
FROM jobs j
JOIN companies c ON j.company_id = c.company_id
WHERE j.city IS NOT NULL 
    AND j.city != ''
    AND j.city != 'Unknown'
    AND c.industry IS NOT NULL 
    AND c.industry != ''
    AND j.city IN (
        SELECT city 
        FROM jobs 
        WHERE city IS NOT NULL AND city != '' AND city != 'Unknown'
        GROUP BY city 
        ORDER BY COUNT(*) DESC 
        LIMIT 5
    )
GROUP BY j.city, c.industry
HAVING COUNT(*) >= 10  -- Only show significant industry presence
ORDER BY j.city, job_count DESC;

-- =====================================================
-- 7. LOCATION TRENDS BY EXPERIENCE LEVEL
-- =====================================================
-- Purpose: Analyze experience level distribution across top locations
-- Expected Output: Experience level breakdown by city

SELECT 
    city,
    experience_level,
    COUNT(*) as job_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY city), 2) as percentage_in_city
FROM jobs 
WHERE city IS NOT NULL 
    AND city != ''
    AND city != 'Unknown'
    AND experience_level IS NOT NULL 
    AND experience_level != ''
    AND city IN (
        SELECT city 
        FROM jobs 
        WHERE city IS NOT NULL AND city != '' AND city != 'Unknown'
        GROUP BY city 
        ORDER BY COUNT(*) DESC 
        LIMIT 5
    )
GROUP BY city, experience_level
ORDER BY city, 
    CASE experience_level 
        WHEN 'Entry' THEN 1 
        WHEN 'Mid' THEN 2 
        WHEN 'Senior' THEN 3 
        ELSE 4 
    END;

-- =====================================================
-- 8. COMPREHENSIVE LOCATION SUMMARY
-- =====================================================
-- Purpose: Create a unified view combining cities and countries analysis
-- Expected Output: Combined location analysis table (max 10 rows)

WITH top_cities AS (
    SELECT 
        'City' as location_type,
        city as location_name,
        COUNT(*) as job_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs WHERE city IS NOT NULL AND city != ''), 2) as percentage_of_category,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) as percentage_of_total
    FROM jobs 
    WHERE city IS NOT NULL AND city != '' AND city != 'Unknown'
    GROUP BY city 
    ORDER BY job_count DESC
    LIMIT 5
),
top_countries AS (
    SELECT 
        'Country' as location_type,
        country as location_name,
        COUNT(*) as job_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs WHERE country IS NOT NULL AND country != ''), 2) as percentage_of_category,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) as percentage_of_total
    FROM jobs 
    WHERE country IS NOT NULL AND country != '' AND country != 'Unknown'
    GROUP BY country 
    ORDER BY job_count DESC
    LIMIT 5
)
SELECT * FROM top_cities
UNION ALL
SELECT * FROM top_countries
ORDER BY job_count DESC
LIMIT 10;

-- =====================================================
-- BUSINESS INSIGHTS QUERIES
-- =====================================================

-- Query to support key business insights
SELECT 
    'Geographic Market Analysis' as analysis_type,
    (SELECT city FROM jobs WHERE city IS NOT NULL AND city != '' AND city != 'Unknown' GROUP BY city ORDER BY COUNT(*) DESC LIMIT 1) as top_city,
    (SELECT COUNT(*) FROM jobs WHERE city = (SELECT city FROM jobs WHERE city IS NOT NULL AND city != '' AND city != 'Unknown' GROUP BY city ORDER BY COUNT(*) DESC LIMIT 1)) as top_city_jobs,
    (SELECT country FROM jobs WHERE country IS NOT NULL AND country != '' AND country != 'Unknown' GROUP BY country ORDER BY COUNT(*) DESC LIMIT 1) as top_country,
    (SELECT COUNT(*) FROM jobs WHERE country = (SELECT country FROM jobs WHERE country IS NOT NULL AND country != '' AND country != 'Unknown' GROUP BY country ORDER BY COUNT(*) DESC LIMIT 1)) as top_country_jobs,
    (SELECT COUNT(*) FROM jobs) as total_jobs;

-- =====================================================
-- END OF LOCATION TRENDS ANALYSIS QUERIES
-- =====================================================