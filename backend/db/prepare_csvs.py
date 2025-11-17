#!/usr/bin/env python3
# backend/db/prepare_csvs.py
"""
Prepare CSVs for database import by:
1. Cleaning empty columns
2. Ensuring proper formatting
3. Setting default weights for sector_metrics
4. Using the populated company_metrics from our research

NOTE: Type definition rows (SERIAL PK, VARCHAR, etc.) should already be removed from source CSVs
"""

import pandas as pd
import os

# Create data directory
os.makedirs('/home/claude/backend_corrected/db/data', exist_ok=True)

print("=" * 80)
print("PREPARING CSVs FOR DATABASE IMPORT")
print("=" * 80)

# 1. SECTORS - Clean and save
print("\n1. Processing sectors...")
sectors = pd.read_csv('/mnt/user-data/uploads/sectors_Sheet1_.csv')
# Remove any extra whitespace from column names
sectors.columns = sectors.columns.str.strip()
# Keep only necessary columns
sectors = sectors[['id', 'sector_name', 'description']]
# Fill NaN descriptions with empty string
sectors['description'] = sectors['description'].fillna('')
sectors.to_csv('/home/claude/backend_corrected/db/data/sectors.csv', index=False)
print(f"   ✓ Saved {len(sectors)} sectors")

# 2. METRICS - Clean and process
print("\n2. Processing metrics...")
metrics = pd.read_csv('/mnt/user-data/uploads/metrics_Sheet1_.csv')
metrics.columns = metrics.columns.str.strip()
# Keep relevant columns
metrics = metrics[['metric_id', 'metric_name', 'unit', 'invert_score', 'description', 'source']]
# Clean NaN values
metrics['description'] = metrics['description'].fillna('')
metrics['source'] = metrics['source'].fillna('')
metrics['invert_score'] = metrics['invert_score'].fillna(False)
metrics.to_csv('/home/claude/backend_corrected/db/data/metrics.csv', index=False)
print(f"   ✓ Saved {len(metrics)} metrics")

# 3. SECTOR_METRICS - Set default weights
print("\n3. Processing sector_metrics...")
sector_metrics = pd.read_csv('/mnt/user-data/uploads/sector_metrics_Sheet1_.csv')
sector_metrics.columns = sector_metrics.columns.str.strip()
sector_metrics = sector_metrics[['sector_metric_id', 'sector_id', 'metric_id', 'weight']]

# Calculate equal weights per sector if not provided
# Group by sector and count metrics
sector_counts = sector_metrics.groupby('sector_id').size()
for sector_id, count in sector_counts.items():
    mask = sector_metrics['sector_id'] == sector_id
    # Set weight to 1/count for equal weighting
    sector_metrics.loc[mask, 'weight'] = sector_metrics.loc[mask, 'weight'].fillna(1.0 / count)

print("\n   Weights per sector:")
for sector_id in sorted(sector_metrics['sector_id'].unique()):
    sector_data = sector_metrics[sector_metrics['sector_id'] == sector_id]
    total_weight = sector_data['weight'].sum()
    print(f"   Sector {sector_id}: {len(sector_data)} metrics, total weight = {total_weight:.4f}")

sector_metrics.to_csv('/home/claude/backend_corrected/db/data/sector_metrics.csv', index=False)
print(f"   ✓ Saved {len(sector_metrics)} sector-metric mappings")

# 4. COMPANIES - Clean
print("\n4. Processing companies...")
companies = pd.read_csv('/mnt/user-data/uploads/companies_Sheet1_.csv')
companies.columns = companies.columns.str.strip()
# Remove empty trailing columns (the ,, at the end)
companies = companies[['company_id', 'name', 'sector_id', 'turnover', 'country', 'description', 'website']]
# Clean NaN values
companies['description'] = companies['description'].fillna('')
companies['website'] = companies['website'].fillna('')
companies['country'] = companies['country'].fillna('UK')  # Default to UK
companies.to_csv('/home/claude/backend_corrected/db/data/companies.csv', index=False)
print(f"   ✓ Saved {len(companies)} companies")

# 5. COMPANY_METRICS - Use the populated version we researched
print("\n5. Processing company_metrics...")
# Use the fully populated version from our research
company_metrics = pd.read_csv('/mnt/user-data/outputs/company_metrics_populated.csv')
company_metrics.to_csv('/home/claude/backend_corrected/db/data/company_metrics.csv', index=False)
print(f"   ✓ Saved {len(company_metrics)} company metrics")

print("\n" + "=" * 80)
print("✅ ALL CSVs PREPARED FOR IMPORT")
print("=" * 80)
print("\nFiles created in: /home/claude/backend_corrected/db/data/")
print("\nNext steps:")
print("1. Run: sudo -u postgres psql -d greenrank -f backend/db/schema.sql")
print("2. Run: ./backend/db/import_data.sh")
print("=" * 80)
