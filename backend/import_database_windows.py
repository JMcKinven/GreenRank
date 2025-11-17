"""
Windows-compatible database import script
Run this instead of reset_database.sh on Windows
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
    
    # Get absolute path
    abs_path = os.path.abspath(file_path)
    
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
    
    # Get count
    count = result.stdout.strip().split()[-1] if result.stdout else "?"
    print(f"✓ Imported {table_name}: {count} rows")
    return True

def main():
    print("=" * 80)
    print("GREENRANK DATABASE IMPORT (WINDOWS)")
    print("=" * 80)
    
    # Check if psql is available
    try:
        subprocess.run(['psql', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n❌ ERROR: psql not found!")
        print("Make sure PostgreSQL is installed and added to PATH")
        print("See setup guide for instructions")
        sys.exit(1)
    
    # Check if data files exist
    data_files = [
        'db/data/sectors.csv',
        'db/data/metrics.csv',
        'db/data/sector_metrics.csv',
        'db/data/companies.csv',
        'db/data/company_metrics.csv'
    ]
    
    for file in data_files:
        if not os.path.exists(file):
            print(f"\n❌ ERROR: File not found: {file}")
            print("Make sure you're in the backend directory")
            sys.exit(1)
    
    print("\n1. Creating database schema...")
    if not run_psql_file('db/schema.sql', 'Schema creation'):
        sys.exit(1)
    
    print("\n2. Importing CSV data...")
    
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
            sys.exit(1)
    
    # Fix sequences
    print("\n3. Fixing sequences...")
    run_psql(
        "SELECT setval('company_metrics_id_seq', (SELECT MAX(id) FROM company_metrics));",
        "Company metrics sequence"
    )
    
    # Verify
    print("\n" + "=" * 80)
    print("VERIFYING DATA")
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
            '-c', query
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout.strip())
    
    print("\n" + "=" * 80)
    print("✅ DATABASE IMPORT COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. python compute_scores.py")
    print("2. python app.py")
    print()

if __name__ == '__main__':
    main()