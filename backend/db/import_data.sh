#!/bin/bash
# backend/db/import_data.sh
# Import all CSV files into PostgreSQL database

set -e  # Exit on error

DBNAME="greenrank"
PGUSER="postgres"
DATA_DIR="$(dirname "$0")/data"

echo "=============================================================================="
echo "IMPORTING CSV DATA INTO DATABASE"
echo "=============================================================================="
echo ""
echo "Database: $DBNAME"
echo "Data directory: $DATA_DIR"
echo ""

# Check if data directory exists
if [ ! -d "$DATA_DIR" ]; then
    echo "❌ ERROR: Data directory not found: $DATA_DIR"
    echo "Run prepare_csvs.py first to create the data files."
    exit 1
fi

# Import in correct order (respecting foreign keys)
echo "1. Importing sectors..."
sudo -u postgres psql -d "$DBNAME" -c "\COPY sectors(id, sector_name, description) FROM '$DATA_DIR/sectors.csv' DELIMITER ',' CSV HEADER;"

echo "2. Importing metrics..."
sudo -u postgres psql -d "$DBNAME" -c "\COPY metrics(metric_id, metric_name, unit, invert_score, description, source) FROM '$DATA_DIR/metrics.csv' DELIMITER ',' CSV HEADER;"

echo "3. Importing sector_metrics..."
sudo -u postgres psql -d "$DBNAME" -c "\COPY sector_metrics(sector_metric_id, sector_id, metric_id, weight) FROM '$DATA_DIR/sector_metrics.csv' DELIMITER ',' CSV HEADER;"

echo "4. Importing companies..."
sudo -u postgres psql -d "$DBNAME" -c "\COPY companies(company_id, name, sector_id, turnover, country, description, website) FROM '$DATA_DIR/companies.csv' DELIMITER ',' CSV HEADER;"

echo "5. Importing company_metrics..."
sudo -u postgres psql -d "$DBNAME" -c "\COPY company_metrics(id, company_id, metric_id, value, year) FROM '$DATA_DIR/company_metrics.csv' DELIMITER ',' CSV HEADER;"

echo ""
echo "=============================================================================="
echo "✅ IMPORT COMPLETE"
echo "=============================================================================="
echo ""
echo "Verifying data..."
echo ""

# Verify import
sudo -u postgres psql -d "$DBNAME" << EOF
SELECT 'Sectors: ' || COUNT(*) FROM sectors;
SELECT 'Metrics: ' || COUNT(*) FROM metrics;
SELECT 'Sector-Metrics: ' || COUNT(*) FROM sector_metrics;
SELECT 'Companies: ' || COUNT(*) FROM companies;
SELECT 'Company Metrics: ' || COUNT(*) FROM company_metrics;
EOF

echo ""
echo "Next step: Run compute_scores.py to calculate sustainability scores"
echo ""
