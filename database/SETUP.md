# Quick Setup Guide

## Step 1: Install Python Dependencies

```bash
cd database

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Mac/Linux
# OR on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Firebase Service Account

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Go to **Project Settings** → **Service Accounts**
4. Click **"Generate New Private Key"**
5. Save the JSON file as `database/config/firebase-credentials.json`

**⚠️ IMPORTANT:** This file contains sensitive credentials. Never commit it to git!

## Step 3: Convert TypeScript Data to CSV (One-time)

```bash
# Make sure venv is activated
python scripts/migrate_from_ts.py
```

This will create:
- `data/countries.csv`
- `data/sites.csv`

## Step 4: Test the CLI

```bash
# Check database connection
python cli.py info

# Validate data
python cli.py validate --file data/sites.csv --schema site

# Dry run (preview without changes)
python cli.py seed --countries data/countries.csv --sites data/sites.csv --dry-run

# Actually seed the database
python cli.py seed --countries data/countries.csv --sites data/sites.csv
```

## Quick Reference

```bash
# Get help
python cli.py --help
python cli.py seed --help

# Seed database (replace all)
python cli.py seed -c data/countries.csv -s data/sites.csv

# Update sites (merge mode)
python cli.py update sites -f data/sites.csv -m merge

# Export current data
python cli.py export all -f csv -o backups/$(date +%Y%m%d)/

# Clear a collection (careful!)
python cli.py clear sites --confirm
```

## Workflow for Updating Data

1. **Export current data** (backup):
   ```bash
   python cli.py export all -f csv -o backups/backup-$(date +%Y%m%d)/
   ```

2. **Edit CSV files** in Excel/Google Sheets

3. **Validate**:
   ```bash
   python cli.py validate -f data/sites.csv -s site
   ```

4. **Preview changes** (dry run):
   ```bash
   python cli.py update sites -f data/sites.csv -m sync --dry-run
   ```

5. **Apply changes**:
   ```bash
   python cli.py update sites -f data/sites.csv -m sync
   ```

## Troubleshooting

**"Firebase credentials not found"**
- Make sure `config/firebase-credentials.json` exists
- Check the file is valid JSON

**"Permission denied"**
- Verify service account has Firestore permissions
- Check you're using the correct project

**"Module not found"**
- Make sure virtual environment is activated: `source venv/bin/activate`
- Re-install dependencies: `pip install -r requirements.txt`
