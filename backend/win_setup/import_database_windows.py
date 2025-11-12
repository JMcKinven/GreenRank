"""
Windows-compatible database import script for GreenRank
Run this instead of reset_database.sh on Windows

Usage:
    python import_database_windows.py

Requirements:
    - PostgreSQL installed and in PATH
    - psql command available
    - CSV files in db/data/ directory
"""

import subprocess
import os
import sys

# Database configuration
DB_NAME = "greenrank"
DB_USER = "greenrank_user"
DB_PASSWORD = "greenrank_pass"
DB_HOST = "localhost"
DB_PORT = "5432"

# Set password in environment
os.environ['PGPASSWORD'] = DB_PASSWORD

def run_psql(command, description):
    """Run a psql command"""
    print(f"\n{description}...")
    result = subprocess.run([
        'psql',
        '-h', DB_HOST,
        '-p', DB_PORT,
        '-U', DB_USER,
        '-d', DB_NAME,
        '-c', command
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    print(f"✓ {description} complete")
    return True

def run_psql_file(file_path, description):
    """Run a SQL file"""
    print(f"\n{description}...")
    result = subprocess.run([
        'psql',
        '-h', DB_HOST,
        '-p', DB_PORT,
        '-U', DB_USER,
        '-d', DB_NAME,
        '-f', file_path
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    print(f"✓ {description} complete")
    return True

def import_csv(table_name, file_path, columns):
    """Import a CSV file into a table"""
    print(f"\nImporting {table_name}...")
    
    # Get absolute path and convert to forward slashes (PostgreSQL requirement)
    abs_path = os.path.abspath(file_path).replace('\\', '/')
    
    # Build COPY command
    copy_command = f"\\COPY {table_name}({columns}) FROM '{abs_path}' DELIMITER ',' CSV HEADER;"
    
    result = subprocess.run([
        'psql',
        '-h', DB_HOST,
        '-p', DB_PORT,
        '-U', DB_USER,
        '-d', DB_NAME,
        '-c', copy_command
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error importing {table_name}: {result.stderr}")
        return False
    
    # Extract count from output
    output = result.stdout.strip()
    if "COPY" in output:
        count = output.split()[-1]
        print(f"✓ Imported {table_name}: {count} rows")
    else:
        print(f"✓ Imported {table_name}")
    
    return True

def main():
    print("=" * 80)
    print("GREENRANK DATABASE IMPORT (WINDOWS)")
    print("=" * 80)
    
    # Check if psql is available
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, check=True, text=True)
        print(f"\nPostgreSQL version: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n❌ ERROR: psql not found!")
        print("\nMake sure:")
        print("1. PostgreSQL is installed")
        print("2. PostgreSQL bin directory is in your PATH")
        print("   (e.g., C:\\Program Files\\PostgreSQL\\16\\bin)")
        print("3. You've restarted VSCode after adding to PATH")
        sys.exit(1)
    
    # Check current directory
    if not os.path.exists('db'):
        print("\n❌ ERROR: 'db' directory not found!")
        print("Make sure you're running this from the 'backend' directory")
        print(f"Current directory: {os.getcwd()}")
        sys.exit(1)
    
    # Check if data files exist
    data_files = [
        'db/data/sectors.csv',
        'db/data/metrics.csv',
        'db/data/sector_metrics.csv',
        'db/data/companies.csv',
        'db/data/company_metrics.csv'
    ]
    
    missing_files = [f for f in data_files if not os.path.exists(f)]
    if missing_files:
        print("\n❌ ERROR: Missing data files:")
        for f in missing_files:
            print(f"  - {f}")
        print("\nMake sure all CSV files are in the db/data/ directory")
        sys.exit(1)
    
    print("\n✓ All prerequisite checks passed")
    
    # Drop and recreate tables
    print("\n" + "=" * 80)
    print("STEP 1: CREATING DATABASE SCHEMA")
    print("=" * 80)
    
    if not run_psql_file('db/schema.sql', 'Creating tables'):
        print("\n❌ Failed to create schema")
        sys.exit(1)
    
    # Import CSV data
    print("\n" + "=" * 80)
    print("STEP 2: IMPORTING CSV DATA")
    print("=" * 80)
    
    # Import in correct order (respecting foreign keys)
    imports = [
        ('sectors', 'db/data/sectors.csv', 'id,sector_name,description'),
        ('metrics', 'db/data/metrics.csv', 'metric_id,metric_name,unit,invert_score,description,source'),
        ('sector_metrics', 'db/data/sector_metrics.csv', 'sector_metric_id,sector_id,metric_id,weight'),
        ('companies', 'db/data/companies.csv', 'company_id,name,sector_id,turnover,country,description,website'),
        ('company_metrics', 'db/data/company_metrics.csv', 'id,company_id,metric_id,value,year'),
    ]
    
    for table, file, columns in imports:
        if not import_csv(table, file, columns):
            print(f"\n❌ Failed to import {table}")
            sys.exit(1)
    
    # Fix sequences
    print("\n" + "=" * 80)
    print("STEP 3: FIXING SEQUENCES")
    print("=" * 80)
    
    run_psql(
        "SELECT setval('company_metrics_id_seq', (SELECT MAX(id) FROM company_metrics));",
        "Fixing company_metrics sequence"
    )
    
    # Verify data
    print("\n" + "=" * 80)
    print("VERIFYING IMPORTED DATA")
    print("=" * 80)
    
    verification_queries = [
        ("SELECT 'Sectors: ' || COUNT(*) FROM sectors", "Sectors"),
        ("SELECT 'Metrics: ' || COUNT(*) FROM metrics", "Metrics"),
        ("SELECT 'Sector-Metrics: ' || COUNT(*) FROM sector_metrics", "Sector-Metrics"),
        ("SELECT 'Companies: ' || COUNT(*) FROM companies", "Companies"),
        ("SELECT 'Company Metrics: ' || COUNT(*) FROM company_metrics", "Company Metrics"),
    ]
    
    print()
    for query, name in verification_queries:
        result = subprocess.run([
            'psql',
            '-h', DB_HOST,
            '-p', DB_PORT,
            '-U', DB_USER,
            '-d', DB_NAME,
            '-t',  # Tuple only (no headers)
            '-A',  # Unaligned output
            '-c', query
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            print(f"  {output}")
        else:
            print(f"  ❌ Error checking {name}")
    
    print("\n" + "=" * 80)
    print("✅ DATABASE IMPORT COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. python compute_scores.py     # Calculate sustainability scores")
    print("  2. python app.py                # Start the API server")
    print("\nAPI will be available at: http://localhost:5000")
    print()

if __name__ == '__main__':
    main()
