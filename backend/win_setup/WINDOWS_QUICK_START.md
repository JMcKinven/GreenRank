# 🪟 **Windows Quick Start Cheat Sheet**

## 📥 **First Time Setup**

```powershell
# 1. Install PostgreSQL from postgresql.org (use password: greenrank_pass)
# 2. Add to PATH: C:\Program Files\PostgreSQL\16\bin
# 3. Restart VSCode

# 4. Create database
psql -U postgres
# Then paste:
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

# 5. Clone & setup project
cd $HOME\Documents
git clone https://github.com/YOUR_USERNAME/GreenRank.git
cd GreenRank\backend

# 6. Python setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 7. Import database
python import_database_windows.py
# Should show: Company Metrics: 2192

# 8. Compute scores
python compute_scores.py

# 9. Start API
python app.py
# Opens on http://localhost:5000
```

---

## 🔄 **Daily Use**

```powershell
# Open VSCode → Open terminal (Ctrl+`)

# Navigate to project
cd $HOME\Documents\GreenRank\backend

# Activate environment
.\venv\Scripts\Activate.ps1

# Start API
python app.py
```

---

## 🧪 **Test API**

```powershell
# Browser: http://localhost:5000/api/health

# Or PowerShell:
Invoke-RestMethod -Uri "http://localhost:5000/api/health"
Invoke-RestMethod -Uri "http://localhost:5000/api/leaderboard"
```

---

## 🔧 **Common Fixes**

### Can't activate venv?
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### psql not found?
```
1. Add to PATH: C:\Program Files\PostgreSQL\16\bin
2. Restart VSCode
3. Test: psql --version
```

### Port 5000 in use?
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### PostgreSQL not running?
```
1. Press Win+R → services.msc
2. Find "postgresql-x64-16"
3. Right-click → Start
```

---

## 📊 **DataGrip Connection**

```
Host:     localhost
Port:     5432
Database: greenrank
User:     greenrank_user
Password: greenrank_pass
```

---

## 🎯 **Key Files**

- **import_database_windows.py** - Import database (Windows)
- **.env** - Configuration (DB credentials)
- **app.py** - Flask API server
- **compute_scores.py** - Calculate scores
- **models.py** - Database models

---

## ✅ **Success Checklist**

- [ ] PostgreSQL installed
- [ ] psql in PATH (test: `psql --version`)
- [ ] Database created (greenrank)
- [ ] Project cloned
- [ ] Venv created and activated `(venv)`
- [ ] Dependencies installed
- [ ] Data imported (2192 metrics)
- [ ] Scores computed (290 companies)
- [ ] API running on port 5000
- [ ] Health check returns "healthy"

---

## 📞 **Quick Commands**

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Deactivate venv
deactivate

# Reimport database
python import_database_windows.py

# Recompute scores
python compute_scores.py

# Start API
python app.py

# Stop API
Ctrl+C

# Check PostgreSQL
sc query postgresql-x64-16

# Connect to database
psql -U greenrank_user -d greenrank
```

---

**See WINDOWS_SETUP_GUIDE.md for detailed instructions**
