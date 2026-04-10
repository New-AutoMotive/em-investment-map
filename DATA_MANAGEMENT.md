# Data Management Guide

## Overview

This project now uses **CSV files as the single source of truth** for all manufacturing site and country data. The Python CLI tool manages all data operations between CSV files and Firebase.

## 📁 Data Structure

```
database/
├── data/              # CSV files (source of truth)
│   ├── countries.csv  # Country statistics
│   └── sites.csv      # Manufacturing sites (343 entries)
├── exports/           # Timestamped backups
├── backups/           # Manual backups
└── cli.py            # Data management tool
```

## 🔄 Data Workflow

```
CSV Files (Edit in Excel/Google Sheets)
    ↓
Python CLI (Push to Firebase)
    ↓
Firebase (Cloud Database)
    ↓
React App (Reads via realtime listeners)
```

## 🛠️ Common Operations

### 1. View Current Data Status
```bash
cd database
python cli.py info
```
**Shows:** Document counts, last updates, collection status

### 2. Export Data from Firebase to CSV
```bash
# Export everything
python cli.py export all -f csv -o data/

# Export specific collection
python cli.py export sites -f csv -o data/sites.csv
python cli.py export countries -f csv -o data/countries.csv
```
**Result:** CSV files in `database/data/` with current Firebase data

### 3. Edit Data (Your Primary Task)
1. Open `database/data/sites.csv` or `countries.csv` in Excel/Google Sheets
2. Make your changes (add, edit, delete rows)
3. Save the file
4. Proceed to Step 4

### 4. Push Changes to Firebase
```bash
# Push sites (sync mode - adds/updates/deletes)
python cli.py update sites -f data/sites.csv -m sync

# Push countries
python cli.py update countries -f data/countries.csv -m sync
```
**Sync mode:** Adds new entries, updates existing, deletes removed entries

### 5. Verify Changes
```bash
python cli.py info
```
Check document counts match your CSV

**In the app:** Refresh browser - changes appear immediately via realtime listeners

## 🎯 Update Modes

| Mode | Behavior |
|------|----------|
| `sync` | **Recommended** - Adds new, updates existing, deletes removed |
| `upsert` | Adds new + updates existing (keeps entries not in CSV) |
| `append` | Only adds new entries (never deletes) |

## 💾 Backups

### Automatic Backups
Every export creates timestamped backup in `exports/`:
```
exports/
├── sites_20260327_143022.csv
└── countries_20260327_143022.csv
```

### Manual Backup
```bash
# Export to backups directory
python cli.py export all -f csv -o backups/backup_$(date +%Y%m%d).csv
```

## ⚠️ Important Notes

1. **Always export before major changes:**
   ```bash
   python cli.py export all -f csv -o data/
   ```
   This ensures you have the latest data

2. **CSV is the source of truth** - Firebase is just the live database

3. **No admin features in app** - All data management via Python CLI

4. **343 sites total** - All have unique IDs (duplicates were fixed)

5. **App updates automatically** - Uses Firebase realtime listeners

## 🔍 Validation

The CLI automatically validates:
- ✅ Required fields present
- ✅ Correct data types
- ✅ Valid coordinates
- ✅ Valid URLs
- ✅ Unique IDs

## 📊 Current Dataset

- **Sites:** 343 manufacturing facilities
- **Countries:** 32 EU/EFTA nations
- **All IDs:** Unique (no duplicates)
- **Export date:** Check `database/data/sites.csv` timestamp

## 🆘 Troubleshooting

### "Duplicate ID" error
Export current data, check CSV for duplicate IDs in first column

### Changes not appearing in app
1. Check Firebase: `python cli.py info`
2. Refresh browser (hard reload: Ctrl+Shift+R)
3. Check browser console for errors

### Lost data
Check `database/exports/` for timestamped backups

## 📝 Example: Add New Site

1. Export current data:
   ```bash
   cd database
   python cli.py export sites -f csv -o data/sites.csv
   ```

2. Open `data/sites.csv` in Excel

3. Add new row with all fields:
   - id: `new-factory-berlin`
   - name: `New Factory Berlin`
   - company: `AutoCorp`
   - country: `DEU`
   - city: `Berlin`
   - latitude: `52.5200`
   - longitude: `13.4050`
   - type: `ev`
   - status: `planned`
   - capacity: `100000`
   - investment: `500000000`
   - employeeCount: `2000`
   - description: `New EV factory in Berlin`

4. Save file

5. Push to Firebase:
   ```bash
   python cli.py update sites -f data/sites.csv -m sync
   ```

6. Verify:
   ```bash
   python cli.py info
   ```
   Should show 344 sites

7. Refresh app - new site appears on map!

---

**Need help?** Run `python cli.py --help` or check `database/README.md`
