
set -e

DBNAME="greenrank"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DATA_DIR="$SCRIPT_DIR/db/data"

echo "=============================================================================="
echo "COMPLETE DATABASE RESET - DROPPING AND RECREATING ALL TABLES"
echo "=============================================================================="
echo ""

# Drop and recreate schema
echo "1. Dropping all existing tables..."
sudo -u postgres psql -d "$DBNAME" << 'EOF'
DROP TABLE IF EXISTS scores CASCADE;
DROP TABLE IF EXISTS company_metrics CASCADE;
DROP TABLE IF EXISTS sector_metrics CASCADE;
DROP TABLE IF EXISTS companies CASCADE;
DROP TABLE IF EXISTS metrics CASCADE;
DROP TABLE IF EXISTS sectors CASCADE;
EOF

echo "   ✓ All tables dropped"
echo ""

echo "2. Creating fresh schema..."
sudo -u postgres psql -d "$DBNAME" -f "$SCRIPT_DIR/db/schema.sql"

echo "   ✓ Schema created"
echo ""

# Import data
echo "3. Importing sectors..."
sudo -u postgres psql -d "$DBNAME" -c "\COPY sectors(id, sector_name, description) FROM '$DATA_DIR/sectors.csv' DELIMITER ',' CSV HEADER;"

echo "4. Importing metrics..."
sudo -u postgres psql -d "$DBNAME" -c "\COPY metrics(metric_id, metric_name, unit, invert_score, description, source) FROM '$DATA_DIR/metrics.csv' DELIMITER ',' CSV HEADER;"

echo "5. Importing sector_metrics..."
sudo -u postgres psql -d "$DBNAME" -c "\COPY sector_metrics(sector_metric_id, sector_id, metric_id, weight) FROM '$DATA_DIR/sector_metrics.csv' DELIMITER ',' CSV HEADER;"

echo "6. Importing companies..."
sudo -u postgres psql -d "$DBNAME" -c "\COPY companies(company_id, name, sector_id, turnover, country, description, website) FROM '$DATA_DIR/companies.csv' DELIMITER ',' CSV HEADER;"

echo "7. Importing company_metrics..."
sudo -u postgres psql -d "$DBNAME" << EOF
-- Import with explicit id
\COPY company_metrics(id, company_id, metric_id, value, year) FROM '$DATA_DIR/company_metrics.csv' DELIMITER ',' CSV HEADER;

-- Fix sequence
SELECT setval('company_metrics_id_seq', (SELECT MAX(id) FROM company_metrics));
EOF

echo ""
echo "=============================================================================="
echo "✅ DATABASE RESET COMPLETE"
echo "=============================================================================="
echo ""
echo "Verifying data..."
echo ""

# Verify import
sudo -u postgres psql -d "$DBNAME" << 'EOF'
SELECT 'Sectors' AS table_name, COUNT(*) AS row_count FROM sectors
UNION ALL
SELECT 'Metrics', COUNT(*) FROM metrics
UNION ALL
SELECT 'Sector-Metrics', COUNT(*) FROM sector_metrics
UNION ALL
SELECT 'Companies', COUNT(*) FROM companies
UNION ALL
SELECT 'Company Metrics', COUNT(*) FROM company_metrics;
EOF

echo ""
echo "=============================================================================="
echo "NEXT STEPS"
echo "=============================================================================="
echo ""
echo "1. Compute sustainability scores:"
echo "   $ source venv/bin/activate"
echo "   $ python3 compute_scores.py"
echo ""
echo "2. Start the API server:"
echo "   $ python3 app.py"
echo ""
