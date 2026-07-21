# Quick GitHub Upload Commands

Follow these steps to upload your project to GitHub:

## Step 1: Verify .gitignore is Working

```powershell
# Check git status
git status

# You should NOT see:
# - .venv/ folder
# - data/nifty100.db
# - output/*.xlsx or output/*.csv
# - reports/**/*.png files
```

## Step 2: Stage All Essential Files

```powershell
# Add all files (gitignore will automatically exclude non-essential ones)
git add .

# Check what will be committed
git status
```

## Step 3: Verify No Large Files

```powershell
# Check for large files (should be empty or small files only)
git diff --cached --stat

# If you see large files (.db, .xlsx), remove them:
# git reset HEAD path/to/large/file
```

## Step 4: Commit Changes

```powershell
git commit -m "Sprint 4 Complete: Dashboard & Valuation Module

- 8-screen Streamlit dashboard
- Valuation module with FCF yield
- Stock screener with 6 presets
- Peer comparison with radar charts
- Complete documentation
- 92 companies supported"
```

## Step 5: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `nifty100-financial-platform`
3. Description: `Production-grade financial analytics for Nifty 100 companies`
4. Choose Public or Private
5. **DO NOT** check "Initialize with README"
6. Click "Create repository"

## Step 6: Push to GitHub

```powershell
# Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/nifty100-financial-platform.git

# Verify remote
git remote -v

# Push to GitHub
git push -u origin main
```

## ✅ What Will Be Uploaded

### Included (Essential):
- ✅ All Python source code (`src/`)
- ✅ Dashboard files (8 screens)
- ✅ Tests (`tests/`)
- ✅ Configuration templates (`config/`)
- ✅ Database schema (`db/schema.sql`)
- ✅ Documentation (all .md files)
- ✅ Requirements (`requirements.txt`)
- ✅ Makefile
- ✅ .gitignore

### Excluded (Automatically by .gitignore):
- ❌ Virtual environment (`.venv/`)
- ❌ Database file (`data/nifty100.db`)
- ❌ Excel data files (`data/raw/*.xlsx`)
- ❌ Output files (`output/*.xlsx`, `output/*.csv`)
- ❌ Report images (`reports/**/*.png`) - 91 files
- ❌ Python cache (`__pycache__/`)
- ❌ Environment variables (`.env`)
- ❌ IDE settings (`.vscode/`, `.idea/`)

## 🔍 Troubleshooting

### Problem: "remote origin already exists"
```powershell
# Remove existing remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/nifty100-financial-platform.git
```

### Problem: "file too large" error
```powershell
# Check which file is large
git ls-files -s | awk '$4 > 10000000 {print $4}'

# Remove large file from staging
git rm --cached path/to/large/file

# Update .gitignore to exclude it
echo "path/to/large/file" >> .gitignore

# Commit again
git commit -m "Remove large files"
```

### Problem: Accidentally committed .venv or data files
```powershell
# Remove from git but keep locally
git rm -r --cached .venv/
git rm --cached data/nifty100.db

# Commit the removal
git commit -m "Remove large files from git"

# Push
git push
```

## 📊 Expected Repository Size

After applying .gitignore:
- **Source code**: ~50 KB
- **Tests**: ~30 KB  
- **Documentation**: ~200 KB
- **Config**: ~10 KB
- **Total**: ~300 KB ✅

## 🎯 Quick One-Liner (After Creating GitHub Repo)

```powershell
git add . && git commit -m "Sprint 4 Complete" && git remote add origin https://github.com/YOUR_USERNAME/nifty100-financial-platform.git && git push -u origin main
```

*(Replace YOUR_USERNAME with your GitHub username)*

---

## ✅ Verification Checklist

Before pushing, verify:

- [ ] `.gitignore` file exists and is committed
- [ ] Ran `git status` - no `.venv/`, `.db`, `.xlsx` files listed
- [ ] Ran `git add .` - only essential files staged
- [ ] Created GitHub repository (empty, no README initialization)
- [ ] Updated remote URL with your username
- [ ] Ready to `git push`

---

## 🎉 After Successful Push

Your GitHub repository will contain:
- ✅ Complete dashboard application
- ✅ All 8 screens functional
- ✅ Valuation analytics module  
- ✅ Stock screener engine
- ✅ Comprehensive documentation
- ✅ Test suite

**Repository size**: ~300 KB (GitHub-friendly!)

Users who clone will need to:
1. Install dependencies: `pip install -r requirements.txt`
2. Add their own data files to `data/` folder
3. Run ETL: `make load`
4. Launch dashboard: `make dashboard`

---

*Quick Reference: https://github.com/YOUR_USERNAME/nifty100-financial-platform*
