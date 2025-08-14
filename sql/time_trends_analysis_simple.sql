-- =====================================================
-- Time Trends Analysis - Simple SQL Version
-- Wuzzuf Job Market Analysis
-- =====================================================
-- Compatible with most SQL databases
-- =====================================================

-- 1. DATA OVERVIEW
-- Get basic statistics about the time range and volume
SELECT 
    'Data Overview' as analysis_type,
    MIN(posting_date) as earliest_date,
    MAX(posting_date) as latest_date,
    COUNT(*) as total_jobs,
    COUNT(DISTINCT posting_year) as unique_years,
    COUNT(DISTINCT posting_month) as unique_months
FROM jobs 
WHERE posting_date IS NOT NULL;

-- 2. TOP 10 MONTHS BY POSTING VOLUME (as per requirements)
SELECT 
    'Top 10 Months' as analysis_type,
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

-- 3. COMPLETE TIME SERIES WITH MONTH-OVER-MONTH ANALYSIS
WITH time_series AS (
    SELECT 
        posting_year,
        posting_month,
        COUNT(*) as posting_count
    FROM jobs 
    WHERE posting_year IS NOT NULL 
        AND posting_month IS NOT NULL
    GROUP BY posting_year, posting_month
    ORDER BY posting_year, posting_month
),
time_series_with_mom AS (
    SELECT *,
        LAG(posting_count) OVER (ORDER BY posting_year, posting_month) as prev_month_count,
        CASE 
            WHEN LAG(posting_count) OVER (ORDER BY posting_year, posting_month) IS NOT NULL 
            THEN ROUND(
                (posting_count - LAG(posting_count) OVER (ORDER BY posting_year, posting_month)) * 100.0 / 
                LAG(posting_count) OVER (ORDER BY posting_year, posting_month), 
                1
            )
            ELSE NULL
        END as mom_change_pct
    FROM time_series
)
SELECT 
    'Time Series' as analysis_type,
    posting_year,
    posting_month,
    posting_count,
    prev_month_count,
    mom_change_pct
FROM time_series_with_mom
ORDER BY posting_year, posting_month;

-- 4. SEASONAL ANALYSIS
SELECT 
    'Seasonal Analysis' as analysis_type,
    posting_month,
    COUNT(*) as total_postings,
    ROUND(AVG(COUNT(*)) OVER(), 0) as avg_monthly_postings,
    CASE 
        WHEN posting_month IN (12, 1, 2) THEN 'Winter'
        WHEN posting_month IN (3, 4, 5) THEN 'Spring'
        WHEN posting_month IN (6, 7, 8) THEN 'Summer'
        WHEN posting_month IN (9, 10, 11) THEN 'Fall'
    END as season
FROM jobs 
WHERE posting_month IS NOT NULL
GROUP BY posting_month
ORDER BY posting_month;

-- 5. SEASONAL SUMMARY
SELECT 
    'Seasonal Summary' as analysis_type,
    CASE 
        WHEN posting_month IN (12, 1, 2) THEN 'Winter'
        WHEN posting_month IN (3, 4, 5) THEN 'Spring'
        WHEN posting_month IN (6, 7, 8) THEN 'Summer'
        WHEN posting_month IN (9, 10, 11) THEN 'Fall'
    END as season,
    COUNT(*) as total_postings,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM jobs 
WHERE posting_month IS NOT NULL
GROUP BY 
    CASE 
        WHEN posting_month IN (12, 1, 2) THEN 'Winter'
        WHEN posting_month IN (3, 4, 5) THEN 'Spring'
        WHEN posting_month IN (6, 7, 8) THEN 'Summer'
        WHEN posting_month IN (9, 10, 11) THEN 'Fall'
    END
ORDER BY total_postings DESC;

-- 6. YEARLY TRENDS
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
        CASE 
            WHEN LAG(total_postings) OVER (ORDER BY posting_year) IS NOT NULL 
            THEN ROUND(
                (total_postings - LAG(total_postings) OVER (ORDER BY posting_year)) * 100.0 / 
                LAG(total_postings) OVER (ORDER BY posting_year), 
                1
            )
            ELSE NULL
        END as yoy_growth_pct
    FROM yearly_data
)
SELECT 
    'Yearly Trends' as analysis_type,
    posting_year,
    total_postings,
    prev_year_postings,
    yoy_growth_pct
FROM yearly_with_growth
ORDER BY posting_year;

-- 7. PEAK AND LOW ACTIVITY IDENTIFICATION
WITH monthly_stats AS (
    SELECT 
        posting_year,
        posting_month,
        COUNT(*) as posting_count
    FROM jobs 
    WHERE posting_year IS NOT NULL 
        AND posting_month IS NOT NULL
    GROUP BY posting_year, posting_month
),
peak_month AS (
    SELECT 
        'Peak Activity' as period_type,
        posting_year,
        posting_month,
        posting_count
    FROM monthly_stats
    WHERE posting_count = (SELECT MAX(posting_count) FROM monthly_stats)
),
low_month AS (
    SELECT 
        'Low Activity' as period_type,
        posting_year,
        posting_month,
        posting_count
    FROM monthly_stats
    WHERE posting_count = (SELECT MIN(posting_count) FROM monthly_stats)
)
SELECT * FROM peak_month
UNION ALL
SELECT * FROM low_month;

-- 8. BUSINESS INSIGHTS SUMMARY
WITH summary_stats AS (
    SELECT 
        COUNT(*) as total_jobs,
        COUNT(DISTINCT posting_year) as years_analyzed,
        COUNT(DISTINCT CONCAT(posting_year, '-', posting_month)) as months_analyzed,
        ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT CONCAT(posting_year, '-', posting_month)), 0) as avg_monthly_postings,
        MAX(posting_year) as latest_year,
        MIN(posting_year) as earliest_year
    FROM jobs 
    WHERE posting_year IS NOT NULL AND posting_month IS NOT NULL
)
SELECT 
    'Summary Statistics' as analysis_type,
    total_jobs,
    years_analyzed,
    months_analyzed,
    avg_monthly_postings,
    earliest_year,
    latest_year
FROM summary_stats;

-- 9. TREND CALCULATION FOR VISUALIZATION
-- This provides data points for creating trend lines
WITH monthly_sequence AS (
    SELECT 
        posting_year,
        posting_month,
        COUNT(*) as posting_count,
        ROW_NUMBER() OVER (ORDER BY posting_year, posting_month) as sequence_number
    FROM jobs 
    WHERE posting_year IS NOT NULL 
        AND posting_month IS NOT NULL
    GROUP BY posting_year, posting_month
    ORDER BY posting_year, posting_month
)
SELECT 
    'Trend Data' as analysis_type,
    sequence_number,
    posting_year,
    posting_month,
    posting_count,
    -- Simple moving average (3-month)
    ROUND(AVG(posting_count) OVER (
        ORDER BY sequence_number 
        ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
    ), 0) as moving_avg_3month
FROM monthly_sequence
ORDER BY sequence_number;