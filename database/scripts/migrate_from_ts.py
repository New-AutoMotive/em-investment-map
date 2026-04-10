#!/usr/bin/env python3
"""
Convert TypeScript data files to CSV format
"""

import re
import json
import sys
from pathlib import Path
import pandas as pd


def parse_ts_array_safe(content: str, variable_name: str) -> list:
    """
    Extract array from TypeScript file using simple regex extraction
    This extracts individual object blocks to avoid parsing issues with complex strings
    """
    import ast
    
    # Find the export statement
    pattern = rf'export\s+const\s+{variable_name}[^=]*=\s*\[([\s\S]*?)\];'
    match = re.search(pattern, content)
    
    if not match:
        raise ValueError(f"Could not find {variable_name} in file")
    
    array_content = match.group(1)
    
    # Extract individual objects using regex
    # Match objects that start with { and end with }
    object_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    objects = re.findall(object_pattern, array_content)
    
    result = []
    for obj_str in objects:
        try:
            # Clean up the object string
            obj_str = re.sub(r"'", '"', obj_str)  # Single to double quotes
            obj_str = re.sub(r'([{,]\s*)(\w+):', r'\1"\2":', obj_str)  # Quote keys
            obj_str = re.sub(r',(\s*[}\]])', r'\1', obj_str)  # Remove trailing commas
            
            # Parse as JSON
            obj = json.loads(obj_str)
            result.append(obj)
        except Exception as e:
            # Skip objects that can't be parsed
            print(f"Warning: Skipping object due to parse error: {str(e)[:50]}")
            continue
    
    return result


def parse_ts_array(content: str, variable_name: str) -> list:
    """
    Extract array from TypeScript file
    
    Args:
        content: File content
        variable_name: Variable name to extract
        
    Returns:
        Parsed array
    """
    # Find the export statement
    pattern = rf'export\s+const\s+{variable_name}[^=]*=\s*(\[[\s\S]*?\]);'
    match = re.search(pattern, content)
    
    if not match:
        raise ValueError(f"Could not find {variable_name} in file")
    
    array_str = match.group(1)
    
    # Convert TypeScript to JSON
    # Replace single quotes with double quotes
    array_str = re.sub(r"'", '"', array_str)
    # Quote unquoted object keys (id: -> "id":) - only match keys, not URLs
    # Match word characters followed by colon, but only after { or comma+whitespace
    array_str = re.sub(r'([{,]\s*)(\w+):', r'\1"\2":', array_str)
    # Remove trailing commas
    array_str = re.sub(r',(\s*[}\]])', r'\1', array_str)
    # Handle multiline strings and comments
    array_str = re.sub(r'//.*$', '', array_str, flags=re.MULTILINE)
    
    # Parse JSON
    try:
        return json.loads(array_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print("Problematic content:")
        print(array_str[:500])
        raise


def convert_countries():
    """Convert seed-countries.ts to CSV"""
    # Get project root (go up from database/scripts/ to project root)
    project_root = Path(__file__).resolve().parent.parent.parent
    ts_file = project_root / 'src' / 'data' / 'seed-countries.ts'
    output_file = Path(__file__).resolve().parent.parent / 'data' / 'countries.csv'
    
    if not ts_file.exists():
        raise FileNotFoundError(f"Could not find {ts_file}\nProject root: {project_root}")
    
    print(f"📊 Converting countries from {ts_file}")
    
    with open(ts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    countries = parse_ts_array(content, 'SEED_COUNTRIES')
    
    # Convert to DataFrame
    df = pd.DataFrame(countries)
    
    # Ensure correct column order
    columns = ['id', 'name', 'chargingDensity', 'evMarketShare', 'description']
    df = df[columns]
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    
    print(f"✅ Converted {len(df)} countries to {output_file}")
    return len(df)


def convert_sites():
    """Convert seed-sites.ts to CSV"""
    # Get project root (go up from database/scripts/ to project root)
    project_root = Path(__file__).resolve().parent.parent.parent
    ts_file = project_root / 'src' / 'data' / 'seed-sites.ts'
    output_file = Path(__file__).resolve().parent.parent / 'data' / 'sites.csv'
    
    if not ts_file.exists():
        raise FileNotFoundError(f"Could not find {ts_file}\nProject root: {project_root}")
    
    print(f"🏭 Converting sites from {ts_file}")
    
    with open(ts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Use a simpler approach - extract only the fields we need
    # This avoids issues with multiline text in extra fields
    sites_raw = parse_ts_array_safe(content, 'SEED_SITES')
    
    # Filter to only the fields we need
    sites = []
    for site in sites_raw:
        clean_site = {
            'id': site.get('id'),
            'name': site.get('name'),
            'countryId': site.get('countryId'),
            'type': site.get('type'),
            'manufacturer': site.get('manufacturer'),
            'location': site.get('location', {}),
        }
        # Only add optional fields if they exist and are simple strings
        if 'produces' in site and isinstance(site.get('produces'), str):
            clean_site['produces'] = site['produces']
        if 'brands' in site and isinstance(site.get('brands'), str):
            clean_site['brands'] = site['brands']
        sites.append(clean_site)
    
    # Flatten nested location
    flattened_sites = []
    for site in sites:
        flat_site = {
            'id': site['id'],
            'name': site['name'],
            'countryId': site['countryId'],
            'type': site['type'],
            'manufacturer': site['manufacturer'],
            'location.lat': site['location']['lat'],
            'location.lng': site['location']['lng'],
        }
        
        # Add optional fields
        if 'produces' in site and site['produces']:
            flat_site['produces'] = site['produces']
        if 'brands' in site and site['brands']:
            flat_site['brands'] = site['brands']
        
        flattened_sites.append(flat_site)
    
    # Convert to DataFrame
    df = pd.DataFrame(flattened_sites)
    
    # Ensure correct column order
    columns = ['id', 'name', 'countryId', 'type', 'manufacturer', 'location.lat', 'location.lng']
    optional_columns = ['produces', 'brands']
    for col in optional_columns:
        if col in df.columns:
            columns.append(col)
    
    df = df[columns]
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    
    print(f"✅ Converted {len(df)} sites to {output_file}")
    return len(df)


def main():
    """Main conversion function"""
    print("\n🔄 TypeScript to CSV Migration")
    print("=" * 50)
    
    try:
        countries_count = convert_countries()
        sites_count = convert_sites()
        
        print("\n✅ Migration Complete!")
        print(f"   Countries: {countries_count}")
        print(f"   Sites: {sites_count}")
        print("=" * 50)
        print("\n💡 CSV files created in database/data/")
        print("   You can now use the CLI tool to seed the database:")
        print("   python cli.py seed --countries data/countries.csv --sites data/sites.csv")
        print("=" * 50 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
