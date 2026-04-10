"""
Sync battery manufacturing projects from Google Cloud SQL (MySQL)
into the Firestore 'sites' collection with type='battery'.

Usage (via CLI):
    python cli.py sync-battery
    python cli.py sync-battery --dry-run
    python cli.py sync-battery --mode replace

Direct usage:
    python scripts/sync_from_sql.py
"""

import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure the database/ root is on the path when run directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.sql_client import CloudSQLClient
from lib.firestore_client import FirestoreClient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Countries that have an active presence on the map
# Sites in other countries will be filtered out of the sync.
# ---------------------------------------------------------------------------
ACTIVE_ISO3_CODES = {
    'AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA',
    'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD',
    'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE', 'ISL', 'LIE', 'NOR', 'CHE',
}

# European bounding box — excludes obviously wrong coordinates (sea, overseas, etc.)
EUROPE_BOUNDS = {
    'lat_min': 34.0,
    'lat_max': 72.0,
    'lng_min': -11.0,
    'lng_max': 35.0,
}

# ---------------------------------------------------------------------------
# Country name → ISO 3166-1 alpha-3 mapping
# The `location_country` field in MySQL contains full English country names.
# ---------------------------------------------------------------------------
COUNTRY_NAME_TO_ISO3: Dict[str, str] = {
    "Albania": "ALB",
    "Austria": "AUT",
    "Belgium": "BEL",
    "Bosnia and Herzegovina": "BIH",
    "Bosnia-Herzegovina": "BIH",
    "Bosnia & Herzegovina": "BIH",
    "Turkey": "TUR",
    "Türkiye": "TUR",
    "Bulgaria": "BGR",
    "Croatia": "HRV",
    "Cyprus": "CYP",
    "Czech Republic": "CZE",
    "Czechia": "CZE",
    "Denmark": "DNK",
    "Estonia": "EST",
    "Finland": "FIN",
    "France": "FRA",
    "Germany": "DEU",
    "Greece": "GRC",
    "Hungary": "HUN",
    "Iceland": "ISL",
    "Ireland": "IRL",
    "Italy": "ITA",
    "Latvia": "LVA",
    "Liechtenstein": "LIE",
    "Lithuania": "LTU",
    "Luxembourg": "LUX",
    "Malta": "MLT",
    "Montenegro": "MNE",
    "Netherlands": "NLD",
    "North Macedonia": "MKD",
    "Norway": "NOR",
    "Poland": "POL",
    "Portugal": "PRT",
    "Romania": "ROU",
    "Serbia": "SRB",
    "Slovakia": "SVK",
    "Slovenia": "SVN",
    "Spain": "ESP",
    "Sweden": "SWE",
    "Switzerland": "CHE",
    "Ukraine": "UKR",
    "United Kingdom": "GBR",
    "UK": "GBR",
    # Some entries may already use ISO codes
    "AUT": "AUT", "BEL": "BEL", "BGR": "BGR", "HRV": "HRV", "CYP": "CYP",
    "CZE": "CZE", "DNK": "DNK", "EST": "EST", "FIN": "FIN", "FRA": "FRA",
    "DEU": "DEU", "GRC": "GRC", "HUN": "HUN", "IRL": "IRL", "ITA": "ITA",
    "LVA": "LVA", "LTU": "LTU", "LUX": "LUX", "MLT": "MLT", "NLD": "NLD",
    "POL": "POL", "PRT": "PRT", "ROU": "ROU", "SVK": "SVK", "SVN": "SVN",
    "ESP": "ESP", "SWE": "SWE", "ISL": "ISL", "LIE": "LIE", "NOR": "NOR",
    "CHE": "CHE", "GBR": "GBR",
}


# ---------------------------------------------------------------------------
# SQL query — joins projects with investments, capacity categories, sectors
# ---------------------------------------------------------------------------
PROJECTS_QUERY = """
SELECT
    p.id,
    p.project_name,
    p.operator,
    CAST(p.latitude AS CHAR)  AS latitude,
    CAST(p.longitude AS CHAR) AS longitude,
    p.location,
    p.location_country,
    p.company_origin_country,
    p.type,
    p.capacity,
    p.capacity_2030,
    p.materials,
    p.processes,
    p.partnerships,
    p.recovery_rate,
    p.opening_year,
    p.jobs_actual,
    p.jobs_2030,
    p.additional_info,
    p.sources,
    s.sector_name,
    cc.category  AS capacity_category,
    cc2.category AS capacity_category_2030,
    oa.area_name AS company_origin_area,
    -- Aggregate investment rows into a single summary string
    GROUP_CONCAT(
        DISTINCT CONCAT(
            COALESCE(pi.currency, ''),
            COALESCE(CAST(pi.amount AS CHAR), ''),
            CASE WHEN pi.investor IS NOT NULL AND pi.investor != ''
                 THEN CONCAT(' (', pi.investor, ')')
                 ELSE ''
            END
        )
        ORDER BY pi.amount DESC
        SEPARATOR '; '
    ) AS investment_summary,
    -- Total investment in EUR (sum of EUR-denominated amounts)
    SUM(CASE WHEN pi.currency = 'EUR' THEN pi.amount ELSE NULL END)
        AS total_investment_eur
FROM projects p
LEFT JOIN sectors           s   ON s.id  = p.sector_id
LEFT JOIN capacity_category cc  ON cc.id = p.capacity_category_id
LEFT JOIN capacity_category cc2 ON cc2.id = p.capacity_category_2030_id
LEFT JOIN origin_area       oa  ON oa.id = p.company_origin_area_id
LEFT JOIN project_investments pi
    ON pi.project_id = p.id
    AND pi.deleted_at IS NULL
WHERE p.deleted_at IS NULL
  AND p.location_country NOT IN ('United Kingdom', 'UK', 'England', 'Scotland', 'Wales')
GROUP BY p.id
ORDER BY p.id
"""


def _slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    text = str(text).lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def _map_country(country_str: Optional[str]) -> Optional[str]:
    """Map a country name or code to ISO3."""
    if not country_str:
        return None
    country_str = country_str.strip()
    iso3 = COUNTRY_NAME_TO_ISO3.get(country_str)
    if not iso3:
        logger.warning(f"Unknown country: '{country_str}' — set to None. Add it to COUNTRY_NAME_TO_ISO3.")
    return iso3


def _format_investment(row: Dict[str, Any]) -> Optional[str]:
    """Build a human-readable investment string from the SQL row."""
    summary = row.get("investment_summary")
    if summary:
        return summary
    return None


def _map_row_to_site(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Map a single SQL row (from PROJECTS_QUERY) to a ManufacturingSite dict.
    Returns None if the row should be excluded.
    """
    project_id = row.get("id")

    # Required: lat/lng — must be valid numbers
    try:
        lat = float(row["latitude"])
        lng = float(row["longitude"])
    except (TypeError, ValueError):
        logger.warning(f"Skipping project id={project_id} — invalid lat/lng")
        return None

    # --- Filter: European bounding box (catches bad/overseas coordinates) ---
    b = EUROPE_BOUNDS
    if not (b['lat_min'] <= lat <= b['lat_max'] and b['lng_min'] <= lng <= b['lng_max']):
        logger.warning(
            f"Skipping project id={project_id} ({row.get('project_name')!r}) — "
            f"coordinates ({lat:.4f}, {lng:.4f}) are outside Europe bounds"
        )
        return None

    # --- Filter: active map countries only ---
    country_id = _map_country(row.get("location_country"))
    if country_id not in ACTIVE_ISO3_CODES:
        logger.info(
            f"Skipping project id={project_id} ({row.get('project_name')!r}) — "
            f"country '{row.get('location_country')}' ({country_id}) not on the map"
        )
        return None

    # --- Name: prefer project_name; fall back to "Operator, City" ---
    raw_name = (row.get("project_name") or "").strip()
    if raw_name:
        name = raw_name
    else:
        operator = (row.get("operator") or "").strip()
        city = (row.get("location") or "").strip()
        if operator and city:
            name = f"{operator}, {city}"
        elif operator:
            name = operator
        elif city:
            name = city
        else:
            name = f"Battery Project {project_id}"

    # Subtype slug (e.g. 'gigafactory', 'recycling')
    raw_type = row.get("type") or ""
    subtype = _slugify(raw_type) if raw_type else None

    # Description
    description_parts = []
    if row.get("additional_info"):
        description_parts.append(row["additional_info"])
    if row.get("processes"):
        description_parts.append(f"Processes: {row['processes']}")
    if row.get("partnerships"):
        description_parts.append(f"Partnerships: {row['partnerships']}")
    description = " | ".join(description_parts) if description_parts else None

    site = {
        "id": f"battery-{project_id}",
        "type": "battery",
        "name": name,
        "manufacturer": row.get("operator") or None,
        "location": {"lat": lat, "lng": lng},
        "countryId": country_id,
        "city": row.get("location") or None,
        "description": description,
        "investmentAmount": _format_investment(row),
        # Dedicated sector field (used for map colour coding)
        "sector": row.get("sector_name") or None,
        # Battery-specific fields
        "subtype": subtype,
        "capacityGwh": row.get("capacity") or None,
        "capacityGwh2030": row.get("capacity_2030") or None,
        "materials": row.get("materials") or None,
        "openingYear": row.get("opening_year") or None,
        "jobsActual": row.get("jobs_actual") or None,
        "jobs2030": row.get("jobs_2030") or None,
        "recoveryRate": row.get("recovery_rate") or None,
        "companyOriginCountry": row.get("company_origin_country") or None,
        "companyOriginArea": row.get("company_origin_area") or None,
        "capacityCategory": row.get("capacity_category") or None,
        "capacityCategory2030": row.get("capacity_category_2030") or None,
    }

    # Strip None values to keep Firestore docs clean, but preserve location
    site = {k: v for k, v in site.items() if v is not None}
    site["location"] = {"lat": lat, "lng": lng}

    return site


def fetch_battery_projects(sql_client: CloudSQLClient) -> List[Dict[str, Any]]:
    """
    Pull all active battery projects from Cloud SQL and return
    them as a list of ManufacturingSite-compatible dicts.
    """
    logger.info("Fetching battery projects from Cloud SQL...")
    rows = sql_client.query(PROJECTS_QUERY)
    logger.info(f"Retrieved {len(rows)} projects from MySQL")

    sites = []
    skipped = 0
    for row in rows:
        site = _map_row_to_site(row)
        if site:
            sites.append(site)
        else:
            skipped += 1

    logger.info(f"Mapped {len(sites)} valid sites ({skipped} skipped)")
    return sites


def sync_battery_to_firestore(
    sql_client: CloudSQLClient,
    firestore_client: FirestoreClient,
    mode: str = "merge",
    dry_run: bool = False,
) -> Dict[str, int]:
    """
    Sync battery projects from Cloud SQL → Firestore 'sites' collection.

    Args:
        sql_client: Connected CloudSQLClient instance
        firestore_client: Initialized FirestoreClient instance
        mode: 'merge' (update+add), 'replace' (delete battery sites + re-add),
              'add-new' (only add new IDs)
        dry_run: If True, show what would happen without writing

    Returns:
        Dict with 'added', 'updated', 'deleted', 'skipped' counts
    """
    results = {"added": 0, "updated": 0, "deleted": 0, "skipped": 0}

    # 1. Fetch from SQL
    new_sites = fetch_battery_projects(sql_client)
    if not new_sites:
        logger.warning("No battery projects fetched — nothing to sync")
        return results

    new_site_map = {s["id"]: s for s in new_sites}
    new_ids = set(new_site_map.keys())

    # 2. Get existing battery sites from Firestore
    logger.info("Reading existing battery sites from Firestore...")
    all_existing = firestore_client.get_collection("sites")
    existing_battery = {
        doc["id"]: doc
        for doc in all_existing
        if doc.get("type") == "battery"
    }
    existing_ids = set(existing_battery.keys())

    logger.info(
        f"Found {len(existing_battery)} existing battery sites in Firestore, "
        f"{len(new_sites)} incoming from SQL"
    )

    # 3. Determine operations
    to_add = new_ids - existing_ids
    to_update = new_ids & existing_ids
    to_delete = existing_ids - new_ids  # only relevant for 'replace' mode

    if mode == "replace":
        # Delete all existing battery sites and re-add everything
        if not dry_run:
            for site_id in existing_ids:
                firestore_client.delete_document("sites", site_id)
            results["deleted"] = len(existing_ids)
            written = firestore_client.batch_set("sites", new_sites)
            results["added"] = written
        else:
            results["deleted"] = len(existing_ids)
            results["added"] = len(new_sites)
            logger.info(
                f"[DRY RUN] Would delete {results['deleted']} and re-add {results['added']} battery sites"
            )

    elif mode == "merge":
        # Update existing + add new (never delete)
        docs_to_write = [new_site_map[i] for i in (to_add | to_update)]
        if not dry_run:
            firestore_client.batch_set("sites", docs_to_write)
        results["added"] = len(to_add)
        results["updated"] = len(to_update)
        if dry_run:
            logger.info(
                f"[DRY RUN] Would add {results['added']} and update {results['updated']} battery sites"
            )

    elif mode == "add-new":
        # Only add sites that don't exist yet
        docs_to_write = [new_site_map[i] for i in to_add]
        if not dry_run and docs_to_write:
            firestore_client.batch_set("sites", docs_to_write)
        results["added"] = len(to_add)
        results["skipped"] = len(to_update)
        if dry_run:
            logger.info(
                f"[DRY RUN] Would add {results['added']} new battery sites "
                f"({results['skipped']} already exist, skipped)"
            )

    return results


if __name__ == "__main__":
    """Allow running this script directly for quick testing."""
    import colorlog

    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s"
    ))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)

    sql = CloudSQLClient()
    with sql:
        sites = fetch_battery_projects(sql)
        print(f"\nFetched {len(sites)} battery sites")
        if sites:
            import json
            print("\nFirst site preview:")
            print(json.dumps(sites[0], indent=2, default=str))
