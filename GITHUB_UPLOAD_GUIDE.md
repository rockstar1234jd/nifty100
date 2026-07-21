# GitHub Upload Guide - Nifty 100 Project

This guide explains what to upload to GitHub and what to exclude.

---

## ✅ Files TO UPLOAD (Essential Files)

### 1. Source Code
```
src/
├── __init__.py
├── analytics/
│   ├── __init__.py
│   ├── ratios.py
│   ├── valuation.py
│   └── capital_allocation.py
├── dashboard/
│   ├── __init__.py
│   ├── app.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── db.py
│   └── pages/
│       ├── __init__.py
│       ├── 01_home.py
│       ├── 02_profile.py
│       ├── 03_screener.py
│       ├── 04_peers.py
│       ├── 05_trends.py
│       ├── 06_sectors.py
│       ├── 07_capital.py
│       └── 08_reports.py
├── etl/
│   ├── __init__.py
│   ├── loader.py
│   ├── normaliser.py
│   └── validator.py
├── screener/
│   ├── __init__.py
│   └── engine.py
├── kpi/
│   ├── __init__.py
│   ├── quality_score.py
│   └── peer_analysis.py
├── api/
│   ├── __init__.py
│   └── main.py
└── reports/
    ├── __init__.py
    └── portfolio_report.py
```

### 2. Configuration Files
```
config/
├── .env.template          # ✅ Template only (not .env)
├── logging_config.yaml
└── screener_config.yaml
```

### 3. Database Schema
```
db/
└── schema.sql
```

### 4. Tests
```
tests/
├── __init__.py
├── etl/
│   └── (all test files)
├── dq/
│   └── (all test files)
├── screener/
│   └── (all test files)
└── kpi/
    └── (all test files)
```

### 5. Documentation
```
├── README.md
├── requirements.txt
├── pytest.ini
├── Makefile
├── SPRINT1_DATA_FOUNDATION.md
├── SPRINT2_RATIO_ENGINE.md
├── SPRINT3_SCREENER_PEER_ENGINE.md
├── SPRINT4_DASHBOARD_VALUATION.md
├── SPRINT4_RETROSPECTIVE.md
├── SPRINT4_COMPLETION_SUMMARY.md
├── GITHUB_UPLOAD_GUIDE.md
└── .gitignore
```

### 6. Empty Directories (with .gitkeep)
```
output/.gitkeep
reports/tearsheets/.gitkeep
reports/sector/.gitkeep
reports/portfolio/.gitkeep
reports/radar_charts/.gitkeep
```

### 7. Notebooks (if any SQL queries)
```
notebooks/
└── exploratory_queries.sql
```

---

## ❌ Files NOT TO UPLOAD (Excluded by .gitignore)

### 1. Data Files (TOO LARGE & SENSITIVE)
```
❌ data/nifty100.db              # ~15MB SQLite database
❌ data/raw/*.xlsx               # Source Excel files
❌ data/supporting/*.xlsx        # Supporting data
```

### 2. Virtual Environment
```
❌ .venv/                        # Python virtual environment
```

### 3. IDE Configuration
```
❌ .vscode/                      # VS Code settings
❌ .idea/                        # PyCharm settings
```

### 4. Generated Output Files
```
❌ output/*.xlsx                 # Generated reports
❌ output/*.csv                  # Generated CSVs
❌ output/*.log                  # Log files
```

### 5. Generated Report Files
```
❌ reports/tearsheets/*.pdf
❌ reports/sector/*.pdf
❌ reports/portfolio/*.pdf
❌ reports/radar_charts/*.png    # ~91 PNG files
```

### 6. Python Cache
```
❌ __pycache__/
❌ *.pyc
❌ .pytest_cache/
```

### 7. Environment Variables
```
❌ .env                          # Contains sensitive keys
```

### 8. Kiro Specs (Optional)
```
❌ .kiro/                        # Kiro spec files
```

---

## 🚀 Step-by-Step Upload Process

### Step 1: Verify .gitignore is working
```bash
# Check what files git will track
git status

# Should NOT see:
# - .venv/
# - data/nifty100.db
# - output/*.xlsx
# - reports/**/*.png
```

### Step 2: Add essential files
```bash
# Add all source code and documentation
git add src/
git add config/
git add tests/
git add db/
git add notebooks/

# Add configuration and documentation
git add .gitignore
git add README.md
git add requirements.txt
git add pytest.ini
git add Makefile
git add *.md

# Add .gitkeep files to preserve directory structure
git add output/.gitkeep
git add reports/**/.gitkeep
```

### Step 3: Check what will be committed
```bash
# Review files to be committed
git status

# See detailed changes
git diff --staged
```

### Step 4: Create initial commit
```bash
git commit -m "Sprint 4 Complete: Dashboard & Valuation Module

- Implemented 8-screen Streamlit dashboard
- Added valuation module with FCF yield analysis
- Complete screener with 6 presets
- Peer comparison with radar charts
- Comprehensive documentation
- 100% coverage of 92 Nifty 100 companies"
```

### Step 5: Create GitHub repository
1. Go to GitHub.com
2. Click "New Repository"
3. Name: `nifty100-financial-platform`
4. Description: "Production-grade financial analytics platform for Nifty 100 companies"
5. Choose: Public or Private
6. **DO NOT** initialize with README (you already have one)
7. Click "Create Repository"

### Step 6: Link to GitHub and push
```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/nifty100-financial-platform.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## 📊 Expected Repository Size

After excluding large files:

| Category | Size |
|----------|------|
| Source Code (src/) | ~50 KB |
| Tests | ~30 KB |
| Documentation | ~200 KB |
| Configuration | ~10 KB |
| **Total** | **~300 KB** |

✅ This is GitHub-friendly (under 1MB)

**Files Excluded** (saved ~100+ MB):
- ❌ Data files: ~50 MB
- ❌ Virtual environment: ~50 MB
- ❌ Generated outputs: ~5 MB
- ❌ Report images: ~5 MB

---

## 🔒 Security Checklist

Before pushing, ensure:

- [ ] `.env` file is NOT included (only `.env.template`)
- [ ] No database files (.db) are included
- [ ] No API keys or passwords in code
- [ ] .gitignore is properly configured
- [ ] Virtual environment (.venv/) is excluded

---

## 📝 Recommended GitHub Repository Settings

### After Upload:

1. **Add Repository Description**
   ```
   Production-grade financial analytics platform for Nifty 100 companies with Streamlit dashboard, valuation module, and stock screener
   ```

2. **Add Topics** (for discoverability)
   ```
   python
   streamlit
   financial-analysis
   stock-screening
   dashboard
   analytics
   nifty100
   plotly
   sqlite
   ```

3. **Add README Sections** (already in README.md)
   - ✅ Installation instructions
   - ✅ Quick start guide
   - ✅ Dashboard screenshots (add if you have any)
   - ✅ Technology stack

4. **Create Releases** (optional)
   - Tag: `v1.0.0`
   - Name: "Sprint 4 - Dashboard & Valuation Complete"

---

## 🎯 What Users Will Need to Do After Cloning

Users who clone your repository will need to:

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup directories**
   ```bash
   make setup
   ```

3. **Provide their own data**
   - Add Excel files to `data/raw/`
   - Add supporting data to `data/supporting/`
   - Run ETL pipeline: `make load`

4. **Create .env file**
   ```bash
   cp config/.env.template .env
   # Edit .env with their settings
   ```

5. **Run dashboard**
   ```bash
   make dashboard
   ```

---

## ⚠️ Common Issues and Solutions

### Issue 1: Large files rejected by GitHub
**Solution**: Ensure .gitignore is applied before committing
```bash
git rm --cached -r data/
git rm --cached -r .venv/
git rm --cached -r output/
git commit -m "Remove large files"
```

### Issue 2: Already committed large files
**Solution**: Use git filter-branch (careful!)
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch data/nifty100.db" \
  --prune-empty --tag-name-filter cat -- --all
```

### Issue 3: Can't push - "file too large"
**Solution**: Check file sizes
```bash
# Find large files
find . -type f -size +10M -not -path "./.git/*" -not -path "./.venv/*"
```

---

## 📋 Quick Command Summary

```bash
# 1. Check current status
git status

# 2. Add essential files
git add .

# 3. Check what will be committed
git status

# 4. Commit
git commit -m "Sprint 4 Complete: Dashboard & Valuation Module"

# 5. Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/nifty100-financial-platform.git

# 6. Push
git push -u origin main
```

---

## ✅ Final Checklist Before Push

- [ ] `.gitignore` file created and working
- [ ] No `.venv/` or `__pycache__/` in commit
- [ ] No `data/nifty100.db` in commit
- [ ] No `.env` file (only `.env.template`)
- [ ] No large Excel files or outputs
- [ ] README.md is comprehensive
- [ ] All source code files included
- [ ] Tests included
- [ ] Documentation included

---

## 🎉 Success!

Once pushed, your repository will contain:
- ✅ Complete source code
- ✅ Dashboard (8 screens)
- ✅ Valuation module
- ✅ Screener engine
- ✅ Tests
- ✅ Documentation
- ✅ Configuration templates

**Total size**: ~300 KB (GitHub-friendly!)

Users can clone and run by providing their own data files.

---

*Last Updated: July 21, 2026*
