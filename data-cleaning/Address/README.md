## Address Data Cleaning & Normalization

This project focuses on cleaning, standardizing, and normalizing address data using Python.  
It simulates a real-world data quality problem commonly found in customer, billing, and logistics datasets.

### Problem
Raw address data often contains:
- Inconsistent formats
- Abbreviations
- Duplicate street types
- Missing or invalid values

This makes analysis and integration with BI tools difficult.

### Solution
A Python-based data cleaning pipeline was developed to:
- Standardize address formats
- Expand abbreviations using a configurable dictionary
- Remove invalid or incomplete records
- Normalize street types, numbers, and orientations
- Generate a clean dataset ready for analysis or BI consumption

### Technologies Used
- Python
- Pandas
- Regular Expressions (regex)
- Excel (input/output)

### Output
The script produces a normalized address dataset that can be directly used in:
- Business Intelligence tools
- Data warehouses
- ETL pipelines

### Skills Demonstrated
- Data Cleaning
- Data Transformation
- Business Rules Implementation
- Text Processing
- ETL Foundations
