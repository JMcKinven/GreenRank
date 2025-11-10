# GreenRank Backend - Complete Setup Guide

**CORRECTED VERSION** - Matches actual CSV structure exactly

---

## 📋 Overview

This backend provides a REST API for the GreenRank sustainability scoring system, including:
- **Database:** PostgreSQL with proper schema matching CSV structure
- **API:** Flask REST API with CORS support
- **Scoring Engine:** Z-score normalization with weighted sector metrics
- **Data:** 290 UK companies with 45 researched, 2,192 sustainability metrics

---

## 🗂️ Project Structure

```
backend/
├── app.py                  # Flask application with all API endpoints
├── config.py               # Database and app configuration
├── models.py               # SQLAlchemy ORM models
├── compute_scores.py       # Scoring calculation engine
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
└── db/
    ├── schema.sql         # PostgreSQL database schema
    ├── prepare_csvs.py    # Clean CSVs for import
    ├── import_data.sh     # Import CSVs into database
    └── data/              # Cleaned CSV files (generated)
        ├── sectors.csv
        ├── metrics.csv
        ├── sector_metrics.csv
        ├── companies.csv
        └── company_metrics.csv
```

---

## ⚙️ Prerequisites

### System Requirements
- **OS:** Ubuntu 20.04+ or similar Linux
- **Python:** 3.8+
- **PostgreSQL:** 12+
- **RAM:** 2GB minimum
- **Disk:** 500MB for database

### Install PostgreSQL
```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable --now postgresql
```

---

## 🚀 Setup Instructions

### Step 1: Create Database and User

```bash
# Switch to postgres user and create database
sudo -u postgres psql << EOF
CREATE USER greenrank_user WITH PASSWORD 'greenrank_pass';
CREATE DATABASE greenrank OWNER greenrank_user;
GRANT ALL PRIVILEGES ON DATABASE greenrank TO greenrank_user;
\c greenrank
GRANT ALL PRIVILEGES ON SCHEMA public TO greenrank_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO greenrank_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO greenrank_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO greenrank_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO greenrank_user;
\q
EOF
```

### Step 2: Create Database Schema

```bash
cd backend
sudo -u postgres psql -d greenrank -f db/schema.sql
```

Expected output: `DROP TABLE`, `CREATE TABLE` messages for each table.

### Step 3: Prepare CSV Data

**Note:** Make sure you've removed the type definition rows (row 2 with `SERIAL PK, VARCHAR, etc.`) from all CSV files first.

```bash
# This cleans the raw CSVs and generates properly formatted files
python3 db/prepare_csvs.py
```

Expected output:
```
✓ Saved 5 sectors
✓ Saved 21 metrics
✓ Saved 38 sector-metric mappings (weights sum to 1.0 per sector)
✓ Saved 290 companies
✓ Saved 2192 company metrics
```

### Step 4: Import Data into Database

```bash
cd db
./import_data.sh
```

Expected output:
```
Sectors: 5
Metrics: 21
Sector-Metrics: 38
Companies: 290
Company Metrics: 2192
```

### Step 5: Setup Python Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 6: Configure Environment

Create `.env` file in `backend/` directory:

```bash
cat > .env << 'EOF'
DB_USER=greenrank_user
DB_PASS=greenrank_pass
DB_HOST=localhost
DB_PORT=5432
DB_NAME=greenrank
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
EOF
```

**⚠️ IMPORTANT:** Never commit `.env` to git!

Add to `.gitignore`:
```bash
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
echo "db/data/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
```

### Step 7: Compute Sustainability Scores

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run scoring engine
python3 compute_scores.py
```

Expected output:
```
📊 Processing Sector 1: finance
   Total weight: 1.0000
   Metric  1 (Operational_energy): 86 values
   ...
   
✅ Computed and saved scores for 290 companies

🏆 TOP 10 COMPANIES (by sector score):
 1. Tesco                    Score:  87.32 (Percentile:  99.7)
 2. Sainsbury's              Score:  85.15 (Percentile:  98.3)
 ...
```

### Step 8: Start Flask API Server

```bash
python3 app.py
```

Expected output:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

---

## 🧪 Test the API

### Using curl

```bash
# Health check
curl http://localhost:5000/api/health

# Get all sectors
curl http://localhost:5000/api/sectors

# Get leaderboard
curl http://localhost:5000/api/leaderboard

# Get specific company
curl http://localhost:5000/api/companies/1

# Search companies
curl "http://localhost:5000/api/companies/search?q=Tesco"

# Get sector leaderboard
curl http://localhost:5000/api/sectors/2/leaderboard
```

### Using browser
Open: http://localhost:5000/api/leaderboard

---

## 📡 API Endpoints Reference

### Sectors
- `GET /api/sectors` - List all sectors
- `GET /api/sectors/:id` - Get sector details with metrics
- `GET /api/sectors/:id/leaderboard` - Ranked companies in sector

### Metrics
- `GET /api/metrics` - List all metrics
- `GET /api/metrics/:id` - Get metric details

### Companies
- `GET /api/companies` - List companies (supports `?sector_id=`, `?limit=`, `?offset=`)
- `GET /api/companies/:id` - Get company with all metrics and scores
- `GET /api/companies/search?q=name` - Search companies by name

### Scores & Rankings
- `GET /api/scores` - All scores (supports `?limit=`)
- `GET /api/leaderboard` - Global leaderboard (default top 50)

### System
- `GET /api/stats` - Overall statistics
- `GET /api/health` - Health check
- `GET /` - API info

---

## 🎯 Scoring Algorithm

### How It Works

1. **Metric Scoring (0-100 scale)**
   - Compare company value to sector distribution
   - Use z-score normalization: `z = (value - mean) / std_dev`
   - Convert to percentile using normal CDF
   - `invert_score=FALSE`: Higher is better (renewable %, recycling %)
   - `invert_score=TRUE`: Lower is better (emissions, waste)

2. **Sector Score**
   - Weighted average of metric scores
   - Weights defined in `sector_metrics` table
   - Missing metrics are excluded from calculation

3. **Global Score**
   - Percentile ranking across all companies
   - 0 = worst, 100 = best

### Example
```
Company: Tesco (Retail)
Renewable Energy: 100% → z-score: +2.1 → Metric Score: 98.2
CO2 Emissions: 1.094M tCO2e → z-score: -0.5 → Metric Score: 69.1
...
Sector Score: 87.32 (weighted average)
Global Score: 99.7 (top 0.3% of all companies)
```

---

## 🐛 Troubleshooting

### Database Connection Errors

**Error:** `psycopg2.OperationalError: could not connect to server`

**Fix:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection settings
sudo -u postgres psql -d greenrank -c "SELECT 1;"
```

### Import Errors

**Error:** `ERROR: column "id" does not exist`

**Fix:** Make sure you ran `prepare_csvs.py` first - it fixes column naming.

### No Scores Computed

**Error:** `❌ No scores computed`

**Fix:**
```bash
# Verify data was imported
sudo -u postgres psql -d greenrank -c "SELECT COUNT(*) FROM company_metrics;"

# Should return 2192
```

### CORS Errors (Frontend)

**Error:** `Access-Control-Allow-Origin` error in browser

**Fix:** Make sure `Flask-CORS` is installed:
```bash
pip install Flask-CORS==4.0.0
```

---

## 🔄 Recomputing Scores

Scores should be recomputed when:
- New company data is added
- Metric values are updated
- Weights are changed

```bash
# Stop Flask server (Ctrl+C)
source venv/bin/activate
python3 compute_scores.py
python3 app.py  # Restart server
```

---

## 📊 Database Schema Quick Reference

```sql
-- Main tables (CSV sources)
sectors           (id, sector_name, description)
metrics           (metric_id, metric_name, unit, invert_score, description, source)
sector_metrics    (sector_metric_id, sector_id, metric_id, weight)
companies         (company_id, name, sector_id, turnover, country, description, website)
company_metrics   (id, company_id, metric_id, value, year)

-- Computed table
scores            (score_id, company_id, sector_score, global_score, last_calculated)
```

---

## 🔐 Production Deployment

For production deployment:

1. **Use strong passwords** - Update `DB_PASS` in `.env`
2. **Disable debug mode** - Set `FLASK_DEBUG=False`
3. **Use HTTPS** - Deploy behind nginx with SSL
4. **Set SECRET_KEY** - Use a random string
5. **Use gunicorn** - Don't use Flask dev server
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
6. **Add authentication** - Protect sensitive endpoints
7. **Rate limiting** - Prevent API abuse
8. **Database backups** - Regular pg_dump

---

## 📝 Notes on CSV Structure

The CSV files are the **source of truth**. Key points:

1. **sectors.csv:** Uses `id` as primary key (not `sector_id`)
2. **metrics.csv:** Has `invert_score` (not `lower_is_better`)
3. **All CSVs:** Have type definition in row 2 (skipped during import)
4. **Weights:** Automatically normalized to sum to 1.0 per sector
5. **company_metrics.csv:** Uses the populated version with 2,192 entries

---

## ✅ Verification Checklist

- [ ] PostgreSQL installed and running
- [ ] Database `greenrank` created
- [ ] User `greenrank_user` has all permissions
- [ ] Schema created (5 tables + scores)
- [ ] CSVs prepared (5 files in db/data/)
- [ ] Data imported (2,192 company metrics)
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file configured
- [ ] Scores computed (290 companies)
- [ ] Flask server running on port 5000
- [ ] API endpoints responding
- [ ] CORS working (if testing with frontend)

---

## 🆘 Support

If you encounter issues:

1. Check logs in terminal
2. Verify database connection: `sudo -u postgres psql -d greenrank`
3. Check data counts match expected values
4. Ensure virtual environment is activated
5. Review error messages carefully

---

**Last Updated:** November 6, 2025  
**Version:** 1.0 (Corrected)  
**Database Schema:** Matches CSV structure exactly
