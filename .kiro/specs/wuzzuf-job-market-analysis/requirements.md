# Requirements Document

## Introduction

This project involves creating a complete, end-to-end data analyst portfolio project using a Wuzzuf job postings dataset. The system will clean and preprocess approximately 25,000 job posting records, store them in a PostgreSQL database, perform comprehensive analysis to answer 6 specific business questions, create visualizations, and produce a Power BI dashboard with supporting documentation for a professional portfolio.

## Requirements

### Requirement 1: Data Processing and Cleaning Pipeline

**User Story:** As a data analyst, I want to clean and preprocess the raw Wuzzuf job postings data, so that I have a reliable, normalized dataset for analysis.

#### Acceptance Criteria

1. WHEN the raw CSV file is loaded THEN the system SHALL remove unnecessary columns like "Unnamed: 0"
2. WHEN duplicate records are detected THEN the system SHALL remove duplicates based on Job Posting ID
3. WHEN processing Job Posting Date THEN the system SHALL parse it into datetime format AND extract year and month columns
4. WHEN processing text fields THEN the system SHALL standardize them by converting to lowercase and stripping whitespace
5. WHEN processing Job Location THEN the system SHALL split it into separate city and country columns where possible
6. WHEN processing Years of Experience THEN the system SHALL convert to integer AND bucket into Entry (0-2 years), Mid (3-5 years), and Senior (6+ years)
7. WHEN processing Job Skills THEN the system SHALL parse string lists into individual skills, normalize to lowercase, remove special characters, AND standardize synonyms
8. WHEN processing salary columns THEN the system SHALL convert Minimum Pay and Maximum Pay to numeric format AND create currency column if applicable
9. WHEN cleaning is complete THEN the system SHALL save three files: jobs.csv, skills.csv, and job_skills.csv

### Requirement 2: Database Storage and Schema Design

**User Story:** As a data analyst, I want to store the cleaned data in a structured PostgreSQL database, so that I can perform efficient queries and analysis.

#### Acceptance Criteria

1. WHEN setting up the database THEN the system SHALL create a PostgreSQL database named "wuzzuf"
2. WHEN creating the schema THEN the system SHALL create tables for jobs, companies, skills, and job_skills with proper relationships
3. WHEN the jobs table is created THEN it SHALL include columns for job_id, date, title, industry, experience_level, salary_min, salary_max, city, country, applicants, and company_id
4. WHEN the companies table is created THEN it SHALL include company_id, name, industry, and size columns
5. WHEN the skills table is created THEN it SHALL include skill_id and skill_name columns
6. WHEN the job_skills table is created THEN it SHALL include job_id and skill_id for many-to-many relationships
7. WHEN data insertion occurs THEN the system SHALL use psycopg2 or sqlalchemy to populate all tables from processed CSV files

### Requirement 3: Business Intelligence Analysis

**User Story:** As a business stakeholder, I want answers to 6 specific business questions about the job market, so that I can make informed decisions about hiring trends and market opportunities.

#### Acceptance Criteria

1. WHEN analyzing top roles and industries THEN the system SHALL identify the most common job titles and hiring industries
2. WHEN analyzing skills demand THEN the system SHALL identify top technical and soft skills overall and by role/industry
3. WHEN analyzing experience requirements THEN the system SHALL show distribution of postings across Entry, Mid, and Senior levels
4. WHEN analyzing salary insights THEN the system SHALL calculate average minimum and maximum salaries by role, industry, and level where salary data exists
5. WHEN analyzing location trends THEN the system SHALL identify top cities and countries by number of postings
6. WHEN analyzing time trends THEN the system SHALL show monthly posting volume trends over time
7. WHEN each analysis is complete THEN the system SHALL produce exactly one table (max 10 rows) and one visualization per business question
8. WHEN analysis is complete THEN the system SHALL provide 2-3 sentence business insights for each question

### Requirement 4: Visualization and Dashboard Creation

**User Story:** As a data analyst, I want to create professional visualizations and an interactive dashboard, so that stakeholders can easily understand and explore the job market insights.

#### Acceptance Criteria

1. WHEN creating Python visualizations THEN the system SHALL use matplotlib, seaborn, or plotly to create charts for each business question
2. WHEN saving visualizations THEN the system SHALL store all charts in the assets/charts/ directory
3. WHEN creating the Power BI dashboard THEN the system SHALL import jobs.csv, skills.csv, and job_skills.csv from data/processed/
4. WHEN designing the dashboard THEN it SHALL be a single-page layout with KPIs for Total Postings, Unique Companies, and Date Range
5. WHEN adding dashboard components THEN it SHALL include bar charts for top roles, industries, and skills, plus donut chart for experience levels
6. WHEN adding dashboard components THEN it SHALL include salary analysis by role, location analysis, and monthly trend line chart
7. WHEN adding interactivity THEN the dashboard SHALL include slicers for industry, level, city, and month
8. WHEN dashboard is complete THEN the system SHALL save as powerbi/wuzzuf_dashboard.pbix AND export 2-3 screenshots

### Requirement 5: SQL Query Documentation

**User Story:** As a developer, I want documented SQL queries for each business question, so that the analysis can be reproduced and validated.

#### Acceptance Criteria

1. WHEN creating SQL queries THEN the system SHALL write one query per business question with clear comments
2. WHEN queries are written THEN they SHALL match the results from the EDA analysis
3. WHEN queries are complete THEN they SHALL be saved in a queries.sql file in the sql/ directory
4. WHEN queries are documented THEN each SHALL include the business question it answers and expected output format

### Requirement 6: Project Structure and Documentation

**User Story:** As a portfolio reviewer, I want clear project structure and comprehensive documentation, so that I can understand the project scope, methodology, and findings.

#### Acceptance Criteria

1. WHEN organizing the project THEN the system SHALL follow the exact directory structure: data/raw/, data/processed/, notebooks/, sql/, powerbi/, assets/charts/, assets/screenshots/
2. WHEN creating notebooks THEN the system SHALL create 01_data_cleaning.ipynb, 02_eda_analysis.ipynb, and 03_sql_queries.ipynb
3. WHEN creating documentation THEN the system SHALL produce a comprehensive README.md with project description, business questions, tech stack, structure, key findings, and screenshots
4. WHEN documenting dependencies THEN the system SHALL create requirements.txt with all Python libraries
5. WHEN project is complete THEN all deliverables SHALL be properly organized and documented for portfolio presentation
6. WHEN code is written THEN it SHALL be clean, modular, and well-commented throughout all files