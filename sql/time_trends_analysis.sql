-- =====================================================
-- Time Trends Analysis - SQL Script
-- Wuzzuf Job Market Analysis
-- =====================================================
-- This script performs comprehensive time trends analysis
-- to identify seasonal hiring patterns and market trends
-- =====================================================

-- =====================================================
-- 🔍 WUZZUF JOB MARKET - TIME TRENDS ANALYSIS
-- ==================================================

-- =====================================================
-- 1. DATA OVERVIEW
-- =====================================================
-- 📅 DATA OVERVIEW:

SELECT 
    MIN(posting_date) as earliest_date,
    MAX(posting_date) as latest_date,
    COUNT(*) as total_jobs,
    COUNT(DISTINCT posting_year) as unique_years,
    COUNT(DISTINCT posting_month) as unique_months,
    ROUND(COUNT(*)::numeric / COUNT(DISTINCT posting_year * 12 + posting_month), 0) as avg_jobs_per_month
FROM jobs 
WHERE posting_date IS NOT NULL;

-- =====================================================
-- 2. TOP 10 MONTHS BY POSTING VOLUME
-- =====================================================
-- 🔝 TOP 10 MONTHS BY POSTING VOLUME:

SELECT 
    posting_year,
    posting_month,
    TO_CHAR(DATE(posting_year || '-' || posting_month || '-01'), 'Mon YYYY') as month_name,
    COUNT(*) as posting_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage,
    RANK() OVER (ORDER BY COUNT(*) DESC) as rank
FROM jobs 
WHERE posting_year IS NOT NULL 
    AND posting_month IS NOT NULL
GROUP BY posting_year, posting_month
ORDER BY posting_count DESC
LIMIT 10;

-- =====================================================
-- 3. COMPLETE TIME SERIES DATA
-- =====================================================
-- 📊 COMPLETE TIME SERIES DATA:

WITH time_series AS (
    SELECT 
        posting_year,
        posting_month,
        COUNT(*) as posting_count,
        DATE(posting_year || '-' || posting_month || '-01') as period_date
    FROM jobs 
    WHERE posting_year IS NOT NULL 
        AND posting_month IS NOT NULL
    GROUP BY posting_year, posting_month
    ORDER BY posting_year, posting_month
),
time_series_with_stats AS (
    SELECT *,
        LAG(posting_count) OVER (ORDER BY period_date) as prev_month_count,
        ROUND(
            (posting_count - LAG(posting_count) OVER (ORDER BY period_date)) * 100.0 / 
            NULLIF(LAG(posting_count) OVER (ORDER BY period_date), 0), 
            1
        ) as mom_change_pct
    FROM time_series
)
SELECT 
    posting_year,
    posting_month,
    TO_CHAR(period_date, 'Mon YYYY') as month_name,
    posting_count,
    prev_month_count,
    COALESCE(mom_change_pct, 0) as mom_change_percent,
    CASE 
        WHEN mom_change_pct > 0 THEN '📈 +'
        WHEN mom_change_pct < 0 THEN '📉 '
        ELSE '➡️ '
    END || COALESCE(mom_change_pct::text, '0') || '%' as trend_indicator
FROM time_series_with_stats
ORDER BY posting_year, posting_month;

-- =====================================================
-- 4. SEASONAL ANALYSIS
-- =====================================================
-- 🌍 SEASONAL POSTING PATTERNS:

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
    ROUND(AVG(total_postings) OVER(), 0) as avg_monthly_postings,
    CASE 
        WHEN total_postings > AVG(total_postings) OVER() THEN '🔥 Above Average'
        WHEN total_postings < AVG(total_postings) OVER() THEN '❄️ Below Average'
        ELSE '➡️ Average'
    END as performance
FROM seasonal_data
ORDER BY posting_month;

-- =====================================================
-- 5. SEASONAL SUMMARY
-- =====================================================
-- 🌍 SEASONAL SUMMARY:

WITH seasonal_summary AS (
    SELECT 
        CASE 
            WHEN posting_month IN (12, 1, 2) THEN 'Winter'
            WHEN posting_month IN (3, 4, 5) THEN 'Spring'
            WHEN posting_month IN (6, 7, 8) THEN 'Summer'
            WHEN posting_month IN (9, 10, 11) THEN 'Fall'
        END as season,
        COUNT(*) as total_postings
    FROM jobs 
    WHERE posting_month IS NOT NULL
    GROUP BY 
        CASE 
            WHEN posting_month IN (12, 1, 2) THEN 'Winter'
            WHEN posting_month IN (3, 4, 5) THEN 'Spring'
            WHEN posting_month IN (6, 7, 8) THEN 'Summer'
            WHEN posting_month IN (9, 10, 11) THEN 'Fall'
        END
)
SELECT 
    season,
    total_postings,
    ROUND(total_postings * 100.0 / SUM(total_postings) OVER(), 2) as percentage,
    RANK() OVER (ORDER BY total_postings DESC) as rank,
    CASE RANK() OVER (ORDER BY total_postings DESC)
        WHEN 1 THEN '🥇 Most Active'
        WHEN 2 THEN '🥈 Second Most Active'
        WHEN 3 THEN '🥉 Third Most Active'
        WHEN 4 THEN '🏃 Least Active'
    END as activity_level
FROM seasonal_summary
ORDER BY total_postings DESC;

-- =====================================================
-- 6. YEARLY TRENDS
-- =====================================================
-- 📈 YEARLY TRENDS:

WITH yearly_data AS (
    SELECT 
        posting_year,
        COUNT(*) as total_postings
    FROM jobs 
    WHERE posting_year IS NOT NULL
    GROUP BY posting_year
),
yearly_with_growth AS (
    SELECT *,
        LAG(total_postings) OVER (ORDER BY posting_year) as prev_year_postings,
        ROUND(
            (total_postings - LAG(total_postings) OVER (ORDER BY posting_year)) * 100.0 / 
            NULLIF(LAG(total_postings) OVER (ORDER BY posting_year), 0), 
            1
        ) as yoy_growth_pct
    FROM yearly_data
)
SELECT 
    posting_year,
    total_postings,
    prev_year_postings,
    COALESCE(yoy_growth_pct, 0) as yoy_growth_percent,
    CASE 
        WHEN yoy_growth_pct > 10 THEN '🚀 Strong Growth'
        WHEN yoy_growth_pct > 0 THEN '📈 Growth'
        WHEN yoy_growth_pct < -10 THEN '📉 Strong Decline'
        WHEN yoy_growth_pct < 0 THEN '📉 Decline'
        ELSE '➡️ Stable'
    END as trend_status
FROM yearly_with_growth
ORDER BY posting_year;

-- =====================================================
-- 7. PEAK AND LOW ACTIVITY PERIODS
-- =====================================================
-- 🔍 PEAK AND LOW ACTIVITY ANALYSIS:

WITH monthly_stats AS (
    SELECT 
        posting_year,
        posting_month,
        COUNT(*) as posting_count,
        TO_CHAR(DATE(posting_year || '-' || posting_month || '-01'), 'Mon YYYY') as month_name
    FROM jobs 
    WHERE posting_year IS NOT NULL 
        AND posting_month IS NOT NULL
    GROUP BY posting_year, posting_month
),
ranked_months AS (
    SELECT *,
        ROW_NUMBER() OVER (ORDER BY posting_count DESC) as high_rank,
        ROW_NUMBER() OVER (ORDER BY posting_count ASC) as low_rank
    FROM monthly_stats
)
SELECT 
    'Peak Activity' as period_type,
    month_name,
    posting_count,
    '🔥' as indicator
FROM ranked_months 
WHERE high_rank <= 3

UNION ALL

SELECT 
    'Low Activity' as period_type,
    month_name,
    posting_count,
    '❄️' as indicator
FROM ranked_months 
WHERE low_rank <= 3

ORDER BY 
    period_type,
    posting_count DESC;

-- =====================================================
-- 8. BUSINESS INSIGHTS SUMMARY
-- =====================================================
-- 💼 BUSINESS INSIGHTS SUMMARY:

-- Overall Statistics
SELECT 
    'Overall Statistics' as insight_type,
    COUNT(*) as total_jobs,
    COUNT(DISTINCT posting_year) as years_analyzed,
    COUNT(DISTINCT posting_year * 12 + posting_month) as months_analyzed,
    ROUND(COUNT(*)::numeric / COUNT(DISTINCT posting_year * 12 + posting_month), 0) as avg_monthly_postings
FROM jobs 
WHERE posting_year IS NOT NULL AND posting_month IS NOT NULL;

-- Peak Month
SELECT 
    'Peak Month' as insight_type,
    posting_year,
    posting_month,
    TO_CHAR(DATE(posting_year || '-' || posting_month || '-01'), 'Mon YYYY') as month_name,
    COUNT(*) as posting_count
FROM jobs 
WHERE posting_year IS NOT NULL AND posting_month IS NOT NULL
GROUP BY posting_year, posting_month
ORDER BY COUNT(*) DESC
LIMIT 1;

-- Lowest Month
SELECT 
    'Lowest Month' as insight_type,
    posting_year,
    posting_month,
    TO_CHAR(DATE(posting_year || '-' || posting_month || '-01'), 'Mon YYYY') as month_name,
    COUNT(*) as posting_count
FROM jobs 
WHERE posting_year IS NOT NULL AND posting_month IS NOT NULL
GROUP BY posting_year, posting_month
ORDER BY COUNT(*) ASC
LIMIT 1;

-- =====================================================
-- 9. BUSINESS RECOMMENDATIONS
-- =====================================================
-- 🎯 BUSINESS RECOMMENDATIONS:

-- Most and Least Active Seasons for Strategic Planning
WITH seasonal_ranks AS (
    SELECT 
        CASE 
            WHEN posting_month IN (12, 1, 2) THEN 'Winter'
            WHEN posting_month IN (3, 4, 5) THEN 'Spring'
            WHEN posting_month IN (6, 7, 8) THEN 'Summer'
            WHEN posting_month IN (9, 10, 11) THEN 'Fall'
        END as season,
        COUNT(*) as total_postings,
        RANK() OVER (ORDER BY COUNT(*) DESC) as season_rank
    FROM jobs 
    WHERE posting_month IS NOT NULL
    GROUP BY 
        CASE 
            WHEN posting_month IN (12, 1, 2) THEN 'Winter'
            WHEN posting_month IN (3, 4, 5) THEN 'Spring'
            WHEN posting_month IN (6, 7, 8) THEN 'Summer'
            WHEN posting_month IN (9, 10, 11) THEN 'Fall'
        END
)
SELECT 
    season,
    total_postings,
    season_rank,
    CASE 
        WHEN season_rank = 1 THEN '🎯 Focus recruitment during this season (highest activity)'
        WHEN season_rank = 4 THEN '💡 Consider strategic hiring during this season (lowest competition)'
        ELSE '📊 Moderate activity season'
    END as recommendation
FROM seasonal_ranks
ORDER BY season_rank;

-- =====================================================
-- ✅ Time Trends Analysis Complete!
-- =====================================================