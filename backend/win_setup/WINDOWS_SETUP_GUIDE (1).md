# 🪟 **GreenRank Backend - Complete Windows Setup Guide**

> **No WSL Required!** Native Windows installation with PostgreSQL.

---

## 📋 **Prerequisites**

- Windows 10/11
- Admin rights on your computer
- VSCode installed
- Git installed

---

## 🚀 **Part 1: Install PostgreSQL**

### **Step 1: Download PostgreSQL**

1. Go to: **https://www.postgresql.org/download/windows/**
2. Click **"Download the installer"**
3. Download **PostgreSQL 16** (or latest version)
4. Run the installer as **Administrator**

### **Step 2: PostgreSQL Installation Wizard**

Follow the wizard:

| Screen | What to do |
|--------|-----------|
| **Setup** | Click Next |
| **Installation Directory** | Keep default: `C:\Program Files\PostgreSQL\16` |
| **Select Components** | ✅ Keep all checked (PostgreSQL Server, pgAdmin, Command Line Tools) |
| **Data Directory** | Keep default: `C:\Program Files\PostgreSQL\16\data` |
| **Password** | Enter: `greenrank_pass` ⚠️ **Remember this!** |
| **Port** | Keep default: `5432` |
| **Advanced Options** | Keep default locale |
| **Pre Installation Summary** | Click Next |
| **Stack Builder** | ❌ Uncheck "Launch Stack Builder" → Click Finish |

✅ **PostgreSQL is now installed!**

---

### **Step 3: Add PostgreSQL to PATH**

1. Press **Win + R**
2. Type `sysdm.cpl` and press Enter
3. Click **"Advanced"** tab
4. Click **"Environment Variables"**
5. Under **"System variables"**, find **"Path"**
6. Click **"Edit"**
7. Click **"New"**
8. Add: `C:\Program Files\PostgreSQL\16\bin`
9. Click **"OK"** on all dialogs
10. **Restart VSCode** (important!)

### **Verify PATH was added:**

Open **Command Prompt** (Win + R → `cmd`):

```cmd
psql --version
```

Should show: `psql (PostgreSQL) 16.x`

---

## 🗄️ **Part 2: Setup Database**

### **Step 1: Start pgAdmin (Optional - for visual management)**

1. Press **Windows key**
2. Search for **"pgAdmin 4"**
3. Open it (will open in browser)
4. Enter master password: `greenrank_pass`

You can use this to view your database later!

---

### **Step 2: Create Database via Command Line**

Open **Command Prompt** as **Administrator**:

```cmd
psql -U postgres
```

Enter password: `greenrank_pass`

You should see:
```
postgres=#
```

Now paste this entire block:

```sql
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
```

You should see:
```
CREATE ROLE
CREATE DATABASE
GRANT
You are now connected to database "greenrank"
GRANT
...
```

✅ **Database created!**

---

## 📥 **Part 3: Clone Project**

Open **VSCode** integrated terminal (`` Ctrl+` ``):

```powershell
# Navigate to your Documents folder (or wherever you want)
cd $HOME\Documents

# Clone the repository (replace with your actual URL)
git clone https://github.com/YOUR_USERNAME/GreenRank.git

# Navigate to backend
cd GreenRank\backend
```

---

## 🐍 **Part 4: Setup Python**

### **Step 1: Check Python is Installed**

In VSCode terminal:

```powershell
python --version
```

Should show `Python 3.8+`

**If not installed:** Download from https://www.python.org/downloads/

---

### **Step 2: Create Virtual Environment**

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1
```

**If you get an error about execution policy:**

```powershell
# Run this first (as Admin):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again:
.\venv\Scripts\Activate.ps1
```

You should now see `(venv)` in your terminal prompt.

---

### **Step 3: Install Dependencies**

```powershell
# Make sure (venv) is active
pip install -r requirements.txt
```

Should install: Flask, SQLAlchemy, psycopg2, etc.

---

## 📊 **Part 5: Import Database Schema & Data**

### **Step 1: Create Windows Import Script**

Create a new file `import_database_windows.py` in the `backend` folder:

```python
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
```

---

### **Step 2: Run the Import Script**

In VSCode terminal (with `(venv)` active):

```powershell
python import_database_windows.py
```

**Expected output:**

```
================================================================================
GREENRANK DATABASE IMPORT (WINDOWS)
================================================================================

1. Creating database schema...
✓ Schema creation complete

2. Importing CSV data...

Importing sectors...
✓ Imported sectors: 5 rows

Importing metrics...
✓ Imported metrics: 21 rows

Importing sector_metrics...
✓ Imported sector_metrics: 38 rows

Importing companies...
✓ Imported companies: 290 rows

Importing company_metrics...
✓ Imported company_metrics: 2192 rows

3. Fixing sequences...
✓ Company metrics sequence complete

================================================================================
VERIFYING DATA
================================================================================

Sectors: 5
Metrics: 21
Sector-Metrics: 38
Companies: 290
Company Metrics: 2192

================================================================================
✅ DATABASE IMPORT COMPLETE!
================================================================================

Next steps:
1. python compute_scores.py
2. python app.py
```

✅ **If you see 2192 company metrics, you're good!**

---

## 📝 **Part 6: Configure Environment**

### **Create `.env` file**

```powershell
# Copy the example
copy .env.example .env

# The default values work fine, no need to edit
```

**Your `.env` should contain:**

```env
DB_USER=greenrank_user
DB_PASS=greenrank_pass
DB_HOST=localhost
DB_PORT=5432
DB_NAME=greenrank
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
```

---

## 🧮 **Part 7: Compute Sustainability Scores**

In VSCode terminal:

```powershell
# Make sure (venv) is active - you should see (venv) in prompt
python compute_scores.py
```

**Expected output:**

```
================================================================================
COMPUTING SUSTAINABILITY SCORES
================================================================================

📊 Processing Sector 1: finance
   Total weight: 1.0000
   Metric  1 (Operational_energy          ): 86 values
   Metric  2 (Renewable_energy_percent    ): 86 values
   ...

✅ Computed and saved scores for 290 companies

🏆 TOP 10 COMPANIES (by sector score):
 1. Tesco                                 Score:  87.32 (Percentile:  99.7)
 2. Sainsbury's                           Score:  85.15 (Percentile:  98.3)
 3. Churchill China                       Score:  83.47 (Percentile:  97.2)
 ...
================================================================================
```

✅ **Scores computed!**

---

## 🚀 **Part 8: Start the API**

```powershell
python app.py
```

**Expected output:**

```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://YOUR_IP:5000
Press CTRL+C to quit
```

✅ **API is running!**

---

## 🧪 **Part 9: Test the API**

### **Option 1: Browser**

Open your browser and go to:

- **http://localhost:5000/api/health**

Should show:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

- **http://localhost:5000/api/leaderboard**

Should show top companies with scores.

---

### **Option 2: Command Line**

Open a **new terminal** (keep API running in first terminal):

```powershell
# Health check
curl http://localhost:5000/api/health

# Get leaderboard
curl http://localhost:5000/api/leaderboard

# Get specific company (Tesco)
curl http://localhost:5000/api/companies/4

# Search companies
curl "http://localhost:5000/api/companies/search?q=tesco"
```

---

### **Option 3: PowerShell (if curl not available)**

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:5000/api/health"

# Get leaderboard
Invoke-RestMethod -Uri "http://localhost:5000/api/leaderboard"

# Get company
Invoke-RestMethod -Uri "http://localhost:5000/api/companies/4"
```

---

## 🎯 **Part 10: Connect with DataGrip**

1. Open **DataGrip**
2. Click **+** → **Data Source** → **PostgreSQL**
3. Enter:
   - **Host:** `localhost`
   - **Port:** `5432`
   - **Database:** `greenrank`
   - **User:** `greenrank_user`
   - **Password:** `greenrank_pass`
4. Click **Test Connection** → Should say "Successful"
5. Click **OK**

Now you can browse your database visually!

---

## 📋 **Daily Workflow**

Every time you want to work on the project:

```powershell
# 1. Open VSCode
# 2. Open integrated terminal (Ctrl+`)
# 3. Navigate to project
cd $HOME\Documents\GreenRank\backend

# 4. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 5. Start API
python app.py

# Done! API runs on http://localhost:5000
```

**PostgreSQL runs as a Windows service** - it starts automatically when Windows boots!

---

## 🔧 **Troubleshooting**

### **Issue 1: "psql is not recognized"**

**Fix:**

1. Add PostgreSQL to PATH (see Part 1, Step 3)
2. Restart VSCode
3. Verify: `psql --version`

---

### **Issue 2: "password authentication failed"**

**Fix:**

```powershell
# Reset password
psql -U postgres

# At postgres=# prompt:
ALTER USER greenrank_user WITH PASSWORD 'greenrank_pass';
\q
```

---

### **Issue 3: "cannot activate virtual environment"**

**Fix:**

```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Try again
.\venv\Scripts\Activate.ps1
```

---

### **Issue 4: "Port 5000 is already in use"**

**Fix:**

```powershell
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Or change port in app.py (bottom of file):
# app.run(debug=True, host='0.0.0.0', port=5001)
```

---

### **Issue 5: "ModuleNotFoundError"**

**Fix:**

```powershell
# Make sure venv is activated (should see (venv) in prompt)
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

---

### **Issue 6: "Could not connect to database"**

**Fix:**

```powershell
# Check PostgreSQL service is running
# Press Win + R, type: services.msc
# Find "postgresql-x64-16" and make sure it's "Running"

# Or use Command Prompt:
sc query postgresql-x64-16
```

---

### **Issue 7: Import script fails with "File not found"**

**Fix:**

```powershell
# Make sure you're in the backend directory
pwd  # Should show: ...\GreenRank\backend

# Check files exist
dir db\data\*.csv

# Should show 5 CSV files
```

---

## ✅ **Success Checklist**

You're all set when:

- ✅ PostgreSQL installed and running
- ✅ Database `greenrank` created with user `greenrank_user`
- ✅ Project cloned to your computer
- ✅ Virtual environment created and activated (see `(venv)` in prompt)
- ✅ Dependencies installed
- ✅ Database imported (2192 company metrics)
- ✅ Scores computed (290 companies)
- ✅ API starts without errors
- ✅ `http://localhost:5000/api/health` returns `"healthy"`
- ✅ DataGrip connects successfully

---

## 🎓 **Quick Commands Reference**

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Deactivate venv
deactivate

# Start API
python app.py

# Stop API
# Press Ctrl+C

# Recompute scores
python compute_scores.py

# Reimport database
python import_database_windows.py

# Check PostgreSQL service
sc query postgresql-x64-16

# Connect to database
psql -U greenrank_user -d greenrank
# Password: greenrank_pass
```

---

## 🆘 **Still Having Issues?**

### **Check these:**

```powershell
# 1. Is PostgreSQL installed?
psql --version

# 2. Is the service running?
sc query postgresql-x64-16

# 3. Can you connect to database?
psql -U greenrank_user -d greenrank -c "SELECT 1"

# 4. Is Python working?
python --version

# 5. Is venv activated?
# Should see (venv) in your prompt

# 6. Are dependencies installed?
pip list | Select-String "Flask"
```

---

## 📞 **Need Help?**

If you're stuck:

1. Check which step failed
2. Read the error message carefully
3. Look at the troubleshooting section for that error
4. Make sure you followed all steps in order
5. Verify PostgreSQL service is running

---

## 🎉 **You're Done!**

Your GreenRank backend is now running on Windows!

**API Endpoints available at:**
- Health: http://localhost:5000/api/health
- Leaderboard: http://localhost:5000/api/leaderboard
- Company: http://localhost:5000/api/companies/4
- Search: http://localhost:5000/api/companies/search?q=tesco

**Next step:** Build your frontend and connect it to the API! 🚀

---

**Last Updated:** November 2025  
**Platform:** Windows 10/11  
**PostgreSQL Version:** 16  
**Python Version:** 3.8+
