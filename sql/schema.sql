-- Wuzzuf Job Market Analysis Database Schema
-- PostgreSQL Database: wuzzuf
-- Created for comprehensive job market analysis and reporting
-- 
-- Prerequisites: 
-- 1. PostgreSQL server running
-- 2. Database 'wuzzuf' created (run sql/create_database.sql first)
-- 3. Connected to 'wuzzuf' database

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS job_skills CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
DROP TABLE IF EXISTS companies CASCADE;
DROP TABLE IF EXISTS skills CASCADE;

-- Create companies table
-- Stores unique company information extracted from job postings
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL UNIQUE,
    industry VARCHAR(100),
    company_size VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create skills table
-- Stores normalized and categorized skills
CREATE TABLE skills (
    skill_id SERIAL PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    skill_category VARCHAR(50) CHECK (skill_category IN ('technical', 'soft')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create jobs table
-- Main table storing job posting information
CREATE TABLE jobs (
    job_id BIGINT PRIMARY KEY,
    posting_date DATE NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    job_title_full VARCHAR(500),
    job_title_additional VARCHAR(500),
    position_type VARCHAR(50),
    position_level VARCHAR(100),
    years_experience INTEGER CHECK (years_experience >= 0),
    experience_level VARCHAR(20) CHECK (experience_level IN ('Entry', 'Mid', 'Senior')),
    city VARCHAR(100),
    country VARCHAR(100),
    salary_min DECIMAL(12,2) CHECK (salary_min >= 0),
    salary_max DECIMAL(12,2) CHECK (salary_max >= 0),
    pay_rate VARCHAR(20),
    currency VARCHAR(10),
    applicants DECIMAL(10,1) CHECK (applicants >= 0),
    company_id INTEGER REFERENCES companies(company_id) ON DELETE SET NULL,
    posting_year INTEGER CHECK (posting_year >= 2000 AND posting_year <= 2030),
    posting_month INTEGER CHECK (posting_month >= 1 AND posting_month <= 12),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure salary_max >= salary_min when both are present
    CONSTRAINT salary_range_check CHECK (
        salary_min IS NULL OR salary_max IS NULL OR salary_max >= salary_min
    )
);

-- Create job_skills junction table
-- Many-to-many relationship between jobs and skills
CREATE TABLE job_skills (
    job_id BIGINT REFERENCES jobs(job_id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(skill_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (job_id, skill_id)
);

-- Create indexes for performance optimization
-- Jobs table indexes
CREATE INDEX idx_jobs_posting_date ON jobs(posting_date);
CREATE INDEX idx_jobs_job_title ON jobs(job_title);
CREATE INDEX idx_jobs_experience_level ON jobs(experience_level);
CREATE INDEX idx_jobs_city ON jobs(city);
CREATE INDEX idx_jobs_country ON jobs(country);
CREATE INDEX idx_jobs_company_id ON jobs(company_id);
CREATE INDEX idx_jobs_posting_year_month ON jobs(posting_year, posting_month);
CREATE INDEX idx_jobs_salary_range ON jobs(salary_min, salary_max) WHERE salary_min IS NOT NULL;

-- Companies table indexes
CREATE INDEX idx_companies_name ON companies(company_name);
CREATE INDEX idx_companies_industry ON companies(industry);

-- Skills table indexes
CREATE INDEX idx_skills_name ON skills(skill_name);
CREATE INDEX idx_skills_category ON skills(skill_category);

-- Job_skills table indexes
CREATE INDEX idx_job_skills_job_id ON job_skills(job_id);
CREATE INDEX idx_job_skills_skill_id ON job_skills(skill_id);

-- Create views for common queries
-- View for jobs with company information
CREATE VIEW jobs_with_companies AS
SELECT 
    j.*,
    c.company_name,
    c.industry as company_industry,
    c.company_size
FROM jobs j
LEFT JOIN companies c ON j.company_id = c.company_id;

-- View for job skills summary
CREATE VIEW job_skills_summary AS
SELECT 
    j.job_id,
    j.job_title,
    j.experience_level,
    j.city,
    j.country,
    c.company_name,
    c.industry,
    s.skill_name,
    s.skill_category
FROM jobs j
LEFT JOIN companies c ON j.company_id = c.company_id
LEFT JOIN job_skills js ON j.job_id = js.job_id
LEFT JOIN skills s ON js.skill_id = s.skill_id;

-- Add comments for documentation
COMMENT ON TABLE companies IS 'Stores unique company information extracted from job postings';
COMMENT ON TABLE skills IS 'Stores normalized and categorized skills (technical/soft)';
COMMENT ON TABLE jobs IS 'Main table containing all job posting information';
COMMENT ON TABLE job_skills IS 'Junction table for many-to-many relationship between jobs and skills';

COMMENT ON COLUMN jobs.job_id IS 'Unique identifier from original job posting';
COMMENT ON COLUMN jobs.experience_level IS 'Bucketed experience level: Entry (0-2 years), Mid (3-5 years), Senior (6+ years)';
COMMENT ON COLUMN jobs.applicants IS 'Number of applicants for the job posting';
COMMENT ON COLUMN jobs.salary_min IS 'Minimum salary in the specified currency';
COMMENT ON COLUMN jobs.salary_max IS 'Maximum salary in the specified currency';

-- Grant permissions (adjust as needed for your environment)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO wuzzuf_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO wuzzuf_user;