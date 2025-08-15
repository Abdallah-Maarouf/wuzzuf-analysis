# Power BI Import Validation Checklist

## Pre-Import Validation
- [ ] All CSV files are present in data/processed/ directory
- [ ] Files are not corrupted (can open in Excel/text editor)
- [ ] File sizes are reasonable (jobs_powerbi.csv ~8MB)

## Import Process
- [ ] Import skills_powerbi.csv first (~167 rows)
- [ ] Import jobs_powerbi.csv second (~25,000 rows)
- [ ] Import job_skills_powerbi.csv third (~160,000 rows)

## Relationship Setup
- [ ] Create relationship: jobs_powerbi[job_id] ←→ job_skills_powerbi[job_id]
  - Cardinality: One to Many (1:*)
  - Cross filter direction: Single
  
- [ ] Create relationship: skills_powerbi[skill_id] ←→ job_skills_powerbi[skill_id]
  - Cardinality: One to Many (1:*)
  - Cross filter direction: Single

## Data Validation
- [ ] Total job count matches across tables (~25,000)
- [ ] Skill count matches (~167 unique skills)
- [ ] Date range is reasonable
- [ ] No circular relationships detected
- [ ] Sample data looks correct in data view

## Performance Validation
- [ ] Tables load quickly in data view
- [ ] Relationships work correctly
- [ ] No performance warnings in Power BI

## Final Validation
- [ ] Create test visual with job count by experience level
- [ ] Create test visual with top skills
- [ ] Verify filters work across visuals
- [ ] Save and test dashboard performance
