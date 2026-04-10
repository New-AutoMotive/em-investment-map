# Database Management Tool

Python CLI tool for managing Firestore database for the EU E-Mobility Investment Map.

## Features

- 🔥 **Firebase Admin SDK** - Direct Firestore access via service account
- 📊 **CSV Support** - Import/export data using CSV files
- ✅ **Data Validation** - Schema validation before upload
- 🔄 **Smart Merging** - Update existing records, add new ones, delete old ones
- 🧪 **Dry Run Mode** - Preview changes before applying
- 💾 **Backup/Export** - Export current data before modifications
- 📝 **Detailed Logging** - Track all operations

## Setup

### 1. Install Python Dependencies

```bash
cd database
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Firebase Service Account

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Go to Project Settings → Service Accounts
4. Click "Generate New Private Key"
5. Save the JSON file as `database/config/firebase-credentials.json`

**⚠️ IMPORTANT:** Never commit this file to git! It's already in `.gitignore`.

## Usage

### Seed Database (Replace All Data)

```bash
# Seed countries and sites from CSV files
python cli.py seed --countries data/countries.csv --sites data/sites.csv

# Dry run first to preview
python cli.py seed --countries data/countries.csv --sites data/sites.csv --dry-run
```

### Update Collection (Merge Strategy)

```bash
# Update sites with merge strategy
python cli.py update sites --file data/sites.csv --mode merge

# Update with delete strategy (remove records not in CSV)
python cli.py update sites --file data/sites.csv --mode sync

# Add new only (skip existing)
python cli.py update sites --file data/sites.csv --mode add-new
```

### Clear Collection

```bash
# Clear all sites
python cli.py clear sites --confirm

# Clear all countries
python cli.py clear countries --confirm
```

### Export Data

```bash
# Export sites to CSV
python cli.py export sites --format csv --output exports/sites.csv

# Export countries to JSON
python cli.py export countries --format json --output exports/countries.json

# Export all collections
python cli.py export all --format csv --output exports/
```

### Validate Data

```bash
# Validate CSV before upload
python cli.py validate --file data/sites.csv --schema site

# Validate countries
python cli.py validate --file data/countries.csv --schema country
```

## Data Formats

### Countries CSV

Required columns:
- `id` - ISO 3166-1 alpha-3 code (e.g., "DEU", "FRA")
- `name` - Country name
- `chargingDensity` - Charging points per 100km²
- `evMarketShare` - BEV market share percentage (2025)
- `description` - Optional description

### Sites CSV

Required columns:
- `id` - Unique site identifier
- `name` - Site name
- `countryId` - ISO 3166-1 alpha-3 country code
- `type` - Either "battery" or "ev"
- `manufacturer` - Company name
- `location.lat` - Latitude
- `location.lng` - Longitude

Optional columns:
- `produces` - What is produced
- `brands` - Brands manufactured

## Update Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `merge` | Update existing + add new | Default update operation |
| `sync` | Update, add new, delete missing | Keep DB in sync with CSV |
| `add-new` | Only add new records | Preserve existing data |
| `replace` | Delete all + upload new | Complete refresh |

## Directory Structure

```
database/
├── cli.py                    # Main CLI entry point
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── config/
│   ├── .gitignore           # Ignore credentials
│   └── firebase-credentials.json  # Service account (DO NOT COMMIT)
├── data/                    # Input data files
│   ├── countries.csv
│   └── sites.csv
├── exports/                 # Exported data
├── backups/                 # Automatic backups
├── lib/
│   ├── __init__.py
│   ├── firestore_client.py  # Firestore connection
│   ├── csv_parser.py        # CSV operations
│   ├── validators.py        # Data validation
│   └── operations.py        # CRUD operations
└── scripts/
    ├── __init__.py
    └── migrate_from_ts.py   # Convert TypeScript to CSV
```

## Examples

### Complete Workflow

```bash
# 1. Export current data as backup
python cli.py export all --format csv --output backups/$(date +%Y%m%d)/

# 2. Edit data/sites.csv in Excel/Google Sheets
# ... make your changes ...

# 3. Validate changes
python cli.py validate --file data/sites.csv --schema site

# 4. Preview with dry run
python cli.py update sites --file data/sites.csv --mode merge --dry-run

# 5. Apply changes
python cli.py update sites --file data/sites.csv --mode merge

# 6. Verify
python cli.py export sites --format csv --output exports/verify.csv
```

## Security Notes

- Service account credentials provide full database access
- Never commit `firebase-credentials.json` to version control
- Restrict service account permissions in Firebase IAM if needed
- Use dry-run mode before destructive operations

## Troubleshooting

**Permission Denied Errors:**
- Verify service account has Firestore permissions
- Check that you're using the correct project ID
- Ensure database ID matches your Firestore database

**CSV Parse Errors:**
- Check for proper UTF-8 encoding
- Verify column headers match expected schema
- Check for empty required fields

**Connection Issues:**
- Verify internet connection
- Check Firebase project status
- Ensure credentials file is valid JSON
