#!/usr/bin/env python3
"""
dedupe_ev_sites.py

Finds EV manufacturing sites that are co-located with battery manufacturing sites
(within THRESHOLD_KM) and removes the EV duplicate, keeping the battery entry.

Usage:
    # Dry run — show matches, make no changes
    python scripts/dedupe_ev_sites.py

    # Execute — delete the matched EV sites from Firestore
    python scripts/dedupe_ev_sites.py --execute
"""

import argparse
import math
import sys
from pathlib import Path

# Allow running from the database/ directory — use resolve() for absolute paths
# so that FirestoreClient._get_database_id() resolves firebase-applet-config.json correctly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.firestore_client import FirestoreClient

# ── Config ─────────────────────────────────────────────────────────────────────
THRESHOLD_KM = 2.0  # Sites within this distance are considered duplicates


# ── Haversine distance ─────────────────────────────────────────────────────────
def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Return the great-circle distance in km between two lat/lng points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def main():
    parser = argparse.ArgumentParser(
        description="Remove EV sites that duplicate co-located battery sites."
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete the duplicates from Firestore (default: dry run)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=THRESHOLD_KM,
        help=f"Distance threshold in km (default: {THRESHOLD_KM})",
    )
    args = parser.parse_args()

    if not args.execute:
        print("🔍 DRY RUN — no changes will be made (pass --execute to delete)\n")

    # ── Fetch all sites ────────────────────────────────────────────────────────
    print("Connecting to Firestore…")
    client = FirestoreClient()
    all_sites = client.get_collection("sites")
    print(f"Loaded {len(all_sites)} sites total.\n")

    battery_sites = [s for s in all_sites if s.get("type") == "battery"]
    ev_sites      = [s for s in all_sites if s.get("type") == "ev"]

    print(f"  Battery sites : {len(battery_sites)}")
    print(f"  EV sites      : {len(ev_sites)}\n")

    # ── Find duplicates ────────────────────────────────────────────────────────
    duplicates = []  # list of EV site dicts that match a battery site

    for ev in ev_sites:
        ev_loc = ev.get("location", {})
        ev_lat = ev_loc.get("lat")
        ev_lng = ev_loc.get("lng")
        if ev_lat is None or ev_lng is None:
            continue

        for bat in battery_sites:
            bat_loc = bat.get("location", {})
            bat_lat = bat_loc.get("lat")
            bat_lng = bat_loc.get("lng")
            if bat_lat is None or bat_lng is None:
                continue

            dist = haversine_km(ev_lat, ev_lng, bat_lat, bat_lng)
            if dist <= args.threshold:
                duplicates.append({
                    "ev_site": ev,
                    "battery_site": bat,
                    "distance_km": round(dist, 3),
                })
                break  # one match is enough per EV site

    # ── Report ─────────────────────────────────────────────────────────────────
    if not duplicates:
        print("✅ No duplicates found within threshold. Nothing to do.")
        return

    print(f"⚠️  Found {len(duplicates)} EV site(s) that duplicate battery sites:\n")
    print(f"{'EV site':<45} {'Battery site':<45} {'Dist':>7}")
    print("─" * 100)

    for match in duplicates:
        ev  = match["ev_site"]
        bat = match["battery_site"]
        ev_label  = f"{ev.get('name', '?')} [{ev.get('id', '?')}]"
        bat_label = f"{bat.get('name', '?')} [{bat.get('id', '?')}]"
        print(f"  {ev_label:<43}  {bat_label:<43}  {match['distance_km']:>5} km")

    print()

    # ── Execute ────────────────────────────────────────────────────────────────
    if args.execute:
        print(f"🗑️  Deleting {len(duplicates)} EV site(s) from Firestore…\n")
        deleted = 0
        for match in duplicates:
            ev_id = match["ev_site"].get("id")
            ev_name = match["ev_site"].get("name", "?")
            if not ev_id:
                print(f"  ⚠️  Skipping EV site with no id: {ev_name}")
                continue
            client.delete_document("sites", ev_id)
            print(f"  ✖  Deleted EV site: {ev_name} ({ev_id})")
            deleted += 1

        print(f"\n✅ Done. Deleted {deleted} EV site(s).")
    else:
        print("ℹ️  Run with --execute to delete these EV sites.")


if __name__ == "__main__":
    main()
