import pandas as pd
import numpy as np
import ast

# Load the dataset
print("Loading Wuzzuf Jobs Posting dataset...")
df = pd.read_csv('Wuzzuf-Jobs-Posting.csv')

print(f"Dataset shape: {df.shape}")
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")

print("\n" + "="*50)
print("COLUMN INFORMATION")
print("="*50)
print(df.info())

print("\n" + "="*50)
print("COLUMN NAMES")
print("="*50)
for i, col in enumerate(df.columns):
    print(f"{i+1:2d}. {col}")

print("\n" + "="*50)
print("FIRST 3 ROWS")
print("="*50)
print(df.head(3).to_string())

print("\n" + "="*50)
print("MISSING VALUES")
print("="*50)
missing_data = df.isnull().sum()
missing_percent = (missing_data / len(df)) * 100
missing_df = pd.DataFrame({
    'Column': missing_data.index,
    'Missing Count': missing_data.values,
    'Missing %': missing_percent.values
}).sort_values('Missing %', ascending=False)
print(missing_df.to_string(index=False))

print("\n" + "="*50)
print("UNIQUE VALUES COUNT")
print("="*50)
for col in df.columns:
    unique_count = df[col].nunique()
    print(f"{col:30s}: {unique_count:6d} unique values")

print("\n" + "="*50)
print("DATE RANGE")
print("="*50)
if 'Job Posting Date' in df.columns:
    df['Job Posting Date'] = pd.to_datetime(df['Job Posting Date'])
    print(f"Date range: {df['Job Posting Date'].min()} to {df['Job Posting Date'].max()}")
    print(f"Years covered: {df['Job Posting Date'].dt.year.unique()}")

print("\n" + "="*50)
print("SAMPLE JOB SKILLS")
print("="*50)
if 'Job Skills' in df.columns:
    # Look at non-null skills
    skills_sample = df['Job Skills'].dropna().head(5)
    for i, skills in enumerate(skills_sample):
        print(f"Row {i+1}: {skills}")
        try:
            # Try to parse as list
            parsed_skills = ast.literal_eval(skills)
            print(f"  Parsed: {parsed_skills[:5]}...")  # Show first 5 skills
        except:
            print(f"  Could not parse as list")
        print()

print("\n" + "="*50)
print("SALARY DATA SAMPLE")
print("="*50)
salary_cols = ['Minimum Pay', 'Maximum Pay', 'Pay Rate']
for col in salary_cols:
    if col in df.columns:
        non_null = df[col].dropna()
        print(f"{col}:")
        print(f"  Non-null count: {len(non_null)}")
        if len(non_null) > 0:
            print(f"  Sample values: {non_null.head().tolist()}")
            print(f"  Data type: {non_null.dtype}")
        print()

print("\n" + "="*50)
print("LOCATION DATA SAMPLE")
print("="*50)
if 'Job Location' in df.columns:
    locations = df['Job Location'].dropna().head(10)
    print("Sample locations:")
    for loc in locations:
        print(f"  {loc}")

print("\n" + "="*50)
print("COMPANY SIZE CATEGORIES")
print("="*50)
if 'Company Size' in df.columns:
    company_sizes = df['Company Size'].value_counts()
    print(company_sizes)

print("\n" + "="*50)
print("JOB POSITION LEVELS")
print("="*50)
if 'Job Position Level' in df.columns:
    position_levels = df['Job Position Level'].value_counts()
    print(position_levels)

print("\n" + "="*50)
print("TOP INDUSTRIES")
print("="*50)
if 'Company Industry' in df.columns:
    top_industries = df['Company Industry'].value_counts().head(10)
    print(top_industries)

print("\n" + "="*50)
print("YEARS OF EXPERIENCE DISTRIBUTION")
print("="*50)
if 'Years of Experience' in df.columns:
    exp_dist = df['Years of Experience'].value_counts().sort_index()
    print(exp_dist.head(15))

print("\nData exploration complete!")