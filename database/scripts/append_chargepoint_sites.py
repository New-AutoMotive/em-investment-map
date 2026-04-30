"""
One-time script to append EV charge point manufacturer sites to database/data/sites.csv
Run from the database/ directory: python scripts/append_chargepoint_sites.py
"""
import csv
import os

SITES_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'sites.csv')

CHARGEPOINT_ROWS = [
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-siemens-leipzig', 'source': '',
        'evConversionPlans': 'Part of €1bn investment; Heliox integration; Focus on heavy-duty charging solutions.',
        'investmentAmount': '', 'countryId': 'DEU', 'manufacturer': 'SIEMENS AG',
        'location.lat': '50.98', 'location.lng': '12.43',
        'city': 'Leipzig', 'name': 'SIEMENS AG Leipzig',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-abb-valdarno', 'source': '',
        'evConversionPlans': '$30m investment; Doubled production capacity; 16,000 m² manufacturing site.',
        'investmentAmount': '', 'countryId': 'ITA', 'manufacturer': 'ABB E-MOBILITY',
        'location.lat': '43.56', 'location.lng': '11.53',
        'city': 'Valdarno', 'name': 'ABB E-MOBILITY Valdarno',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-alpitronic-bolzano', 'source': '',
        'evConversionPlans': 'Global expansion including USA; Proprietary SiC technology; Regional economic anchor in South Tyrol.',
        'investmentAmount': '', 'countryId': 'ITA', 'manufacturer': 'ALPITRONIC',
        'location.lat': '46.5', 'location.lng': '11.35',
        'city': 'Bolzano', 'name': 'ALPITRONIC Bolzano',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-wallbox-barcelona', 'source': '',
        'evConversionPlans': '€9m investment; 750,000 unit annual capacity; Acquired ABL to expand European footprint.',
        'investmentAmount': '', 'countryId': 'ESP', 'manufacturer': 'WALLBOX',
        'location.lat': '41.39', 'location.lng': '2.17',
        'city': 'Barcelona', 'name': 'WALLBOX Barcelona',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-kempower-lahti', 'source': '',
        'evConversionPlans': 'New 10,000 m² factory; Over 200 new jobs created; Strong municipal partnership in Lahti.',
        'investmentAmount': '', 'countryId': 'FIN', 'manufacturer': 'KEMPOWER',
        'location.lat': '60.98', 'location.lng': '25.66',
        'city': 'Lahti', 'name': 'KEMPOWER Lahti',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-schneider-le-vaudreuil', 'source': '',
        'evConversionPlans': 'WEF Lighthouse factory designation; High-efficiency production; Key training hub for smart energy systems.',
        'investmentAmount': '', 'countryId': 'FRA', 'manufacturer': 'SCHNEIDER ELECTRIC',
        'location.lat': '49.26', 'location.lng': '1.21',
        'city': 'Le Vaudreuil', 'name': 'SCHNEIDER ELECTRIC Le Vaudreuil',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-alfen-almere', 'source': '',
        'evConversionPlans': 'New 24,000 m² headquarters; €500m+ annual revenue; Smart grid integration focus.',
        'investmentAmount': '', 'countryId': 'NLD', 'manufacturer': 'ALFEN',
        'location.lat': '52.35', 'location.lng': '5.26',
        'city': 'Almere', 'name': 'ALFEN Almere',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-ekoenergetyka-zielona-gora', 'source': '',
        'evConversionPlans': '20% share of Polish bus charging market; Doubled turnover; Backed by Enterprise Investors.',
        'investmentAmount': '', 'countryId': 'POL', 'manufacturer': 'EKOENERGETYKA',
        'location.lat': '51.94', 'location.lng': '15.5',
        'city': 'Zielona Góra', 'name': 'EKOENERGETYKA Zielona Góra',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-zaptec-stavanger', 'source': '',
        'evConversionPlans': '€110m annual revenue; Part of strong regional charging cluster with Easee in Stavanger.',
        'investmentAmount': '', 'countryId': 'NOR', 'manufacturer': 'ZAPTEC',
        'location.lat': '58.97', 'location.lng': '5.73',
        'city': 'Stavanger', 'name': 'ZAPTEC Stavanger',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-easee-stavanger', 'source': '',
        'evConversionPlans': 'Regulatory recovery following earlier challenges; Key employer in the Norwegian tech sector.',
        'investmentAmount': '', 'countryId': 'NOR', 'manufacturer': 'EASEE',
        'location.lat': '58.97', 'location.lng': '5.73',
        'city': 'Stavanger', 'name': 'EASEE Stavanger',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-ctek-vikmanshyttan', 'source': '',
        'evConversionPlans': 'Grid management and energy storage focus; Approximately 200 employees; Refocused after GM partnership ended.',
        'investmentAmount': '', 'countryId': 'SWE', 'manufacturer': 'CTEK',
        'location.lat': '60.3', 'location.lng': '15.82',
        'city': 'Vikmanshyttan', 'name': 'CTEK Vikmanshyttan',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-garo-gnosjo', 'source': '',
        'evConversionPlans': 'Manufacturing in Sweden and Poland; Revenue declined in late 2024 amid market headwinds.',
        'investmentAmount': '', 'countryId': 'SWE', 'manufacturer': 'GARO',
        'location.lat': '57.36', 'location.lng': '13.74',
        'city': 'Gnosjö', 'name': 'GARO Gnosjö',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-keba-linz', 'source': '',
        'evConversionPlans': '€514m annual revenue; 2,100 employees; Acquired EnerCharge to strengthen charging portfolio.',
        'investmentAmount': '', 'countryId': 'AUT', 'manufacturer': 'KEBA',
        'location.lat': '48.31', 'location.lng': '14.29',
        'city': 'Linz', 'name': 'KEBA Linz',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-efacec-matosinhos', 'source': '',
        'evConversionPlans': 'Acquired by Mutares; 2,000 employees; Undergoing restructuring to support growth in EV charging.',
        'investmentAmount': '', 'countryId': 'PRT', 'manufacturer': 'EFACEC',
        'location.lat': '41.18', 'location.lng': '-8.69',
        'city': 'Matosinhos', 'name': 'EFACEC Matosinhos',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-delta-dubnica', 'source': '',
        'evConversionPlans': 'Central European hub for Delta Electronics; Deep supply chain integration with parent Taiwanese conglomerate.',
        'investmentAmount': '', 'countryId': 'SVK', 'manufacturer': 'DELTA ELECTRONICS',
        'location.lat': '48.96', 'location.lng': '18.17',
        'city': 'Dubnica nad Váhom', 'name': 'DELTA ELECTRONICS Dubnica nad Váhom',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-enovates-lokeren', 'source': '',
        'evConversionPlans': 'Vehicle-to-Grid specialist; Volatile revenue (€34m to €12m); Strong R&D focus on V2G technology.',
        'investmentAmount': '', 'countryId': 'BEL', 'manufacturer': 'ENOVATES',
        'location.lat': '51.1', 'location.lng': '3.99',
        'city': 'Lokeren', 'name': 'ENOVATES Lokeren',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-elinta-kaunas', 'source': '',
        'evConversionPlans': '€7m investment; Design-led export strategy; Part of the growing Kaunas technology cluster.',
        'investmentAmount': '', 'countryId': 'LTU', 'manufacturer': 'ELINTA CHARGE',
        'location.lat': '54.9', 'location.lng': '23.9',
        'city': 'Kaunas', 'name': 'ELINTA CHARGE Kaunas',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-mc-chargers-thessaloniki', 'source': '',
        'evConversionPlans': 'Acquired by Cosmos Aluminum; Relocating to Sindos industrial zone; Focus on Megawatt Charging System (MCS).',
        'investmentAmount': '', 'countryId': 'GRC', 'manufacturer': 'MC CHARGERS',
        'location.lat': '40.64', 'location.lng': '22.94',
        'city': 'Thessaloniki', 'name': 'MC CHARGERS Thessaloniki',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-dbt-brebieres', 'source': '',
        'evConversionPlans': 'Euronext-listed; Key player in ultrafast public charging hubs across France.',
        'investmentAmount': '', 'countryId': 'FRA', 'manufacturer': 'DBT',
        'location.lat': '50.34', 'location.lng': '3.02',
        'city': 'Brebières', 'name': 'DBT Brebières',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-ads-tec-dresden', 'source': '',
        'evConversionPlans': '20 MW battery storage contracts awarded in 2025; Specialist in grid-buffering ultrafast charging.',
        'investmentAmount': '', 'countryId': 'DEU', 'manufacturer': 'ADS-TEC ENERGY',
        'location.lat': '51.05', 'location.lng': '13.74',
        'city': 'Dresden', 'name': 'ADS-TEC ENERGY Dresden',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-webasto-schierling', 'source': '',
        'evConversionPlans': 'Divested majority of charging business to Transom Capital; Retained minority stake and production facility.',
        'investmentAmount': '', 'countryId': 'DEU', 'manufacturer': 'WEBASTO',
        'location.lat': '48.83', 'location.lng': '12.14',
        'city': 'Schierling', 'name': 'WEBASTO Schierling',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-compleo-dortmund', 'source': '',
        'evConversionPlans': 'Acquired by Kostal Group; Wickede and Wambel sites closed; Dortmund facility retained as production base.',
        'investmentAmount': '', 'countryId': 'DEU', 'manufacturer': 'COMPLEO',
        'location.lat': '51.51', 'location.lng': '7.47',
        'city': 'Dortmund', 'name': 'COMPLEO Dortmund',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-abl-lauf', 'source': '',
        'evConversionPlans': 'Acquired by Wallbox; Continues to focus on DACH market compliance; Family-owned exit following acquisition.',
        'investmentAmount': '', 'countryId': 'DEU', 'manufacturer': 'ABL',
        'location.lat': '49.51', 'location.lng': '11.28',
        'city': 'Lauf an der Pegnitz', 'name': 'ABL Lauf an der Pegnitz',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-heliox-best', 'source': '',
        'evConversionPlans': 'Acquired by Siemens; 330 employees; Leading position in heavy-duty and bus depot charging.',
        'investmentAmount': '', 'countryId': 'NLD', 'manufacturer': 'HELIOX',
        'location.lat': '51.51', 'location.lng': '5.39',
        'city': 'Best', 'name': 'HELIOX Best',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-go-e-feldkirchen', 'source': '',
        'evConversionPlans': '80 employees; Management pivot towards export markets; SME success story in Austrian tech sector.',
        'investmentAmount': '', 'countryId': 'AUT', 'manufacturer': 'GO-E',
        'location.lat': '46.72', 'location.lng': '14.1',
        'city': 'Feldkirchen', 'name': 'GO-E Feldkirchen',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-smart-electric-jaunmarupe', 'source': '',
        'evConversionPlans': 'Supported by Latvian Investment and Development Agency (LIAA); 2,000+ installations; Exporting to US and EU markets.',
        'investmentAmount': '', 'countryId': 'LVA', 'manufacturer': 'SMART ELECTRIC TECH',
        'location.lat': '56.88', 'location.lng': '24.05',
        'city': 'Jaunmarupe', 'name': 'SMART ELECTRIC TECH Jaunmarupe',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-zpue-wloszczowa', 'source': '',
        'evConversionPlans': 'Large utility infrastructure supplier; Integrated energy storage and charging solutions; Major regional employer.',
        'investmentAmount': '', 'countryId': 'POL', 'manufacturer': 'ZPUE',
        'location.lat': '50.85', 'location.lng': '19.97',
        'city': 'Wloszczowa', 'name': 'ZPUE Wloszczowa',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-enelion-gdansk', 'source': '',
        'evConversionPlans': '60 employees; $1.3m funding round; Focus on smart AC charging and energy management.',
        'investmentAmount': '', 'countryId': 'POL', 'manufacturer': 'ENELION',
        'location.lat': '54.35', 'location.lng': '18.65',
        'city': 'Gdansk', 'name': 'ENELION Gdansk',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-voltdrive-prostejov', 'source': '',
        'evConversionPlans': 'Component manufacturing for EV charging; Integrated into the Central European automotive supply chain.',
        'investmentAmount': '', 'countryId': 'CZE', 'manufacturer': 'VOLTDRIVE',
        'location.lat': '49.47', 'location.lng': '17.11',
        'city': 'Prostejov', 'name': 'VOLTDRIVE Prostejov',
    },
    {
        'brands': '', 'sourceUrl': '', 'type': 'chargepoint',
        'produces': 'EV Charging Equipment',
        'id': 'chargepoint-olife-prague', 'source': '',
        'evConversionPlans': 'Battery storage integration specialist; Powered by Olife proprietary technology; Focus on grid balancing solutions.',
        'investmentAmount': '', 'countryId': 'CZE', 'manufacturer': 'OLIFE ENERGY',
        'location.lat': '50.08', 'location.lng': '14.43',
        'city': 'Prague', 'name': 'OLIFE ENERGY Prague',
    },
]

FIELDNAMES = [
    'brands', 'sourceUrl', 'type', 'produces', 'id', 'source',
    'evConversionPlans', 'investmentAmount', 'countryId', 'manufacturer',
    'location.lat', 'location.lng', 'city', 'name'
]

# Check for duplicates before appending
with open(SITES_CSV, 'r', encoding='utf-8') as f:
    existing = list(csv.DictReader(f))

existing_ids = {row['id'] for row in existing}
new_rows = [r for r in CHARGEPOINT_ROWS if r['id'] not in existing_ids]
skipped = len(CHARGEPOINT_ROWS) - len(new_rows)

if skipped:
    print(f"Skipping {skipped} rows already present in CSV.")

if not new_rows:
    print("No new rows to append. All chargepoint sites already exist in sites.csv.")
else:
    with open(SITES_CSV, 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction='ignore')
        for row in new_rows:
            writer.writerow(row)
    print(f"Successfully appended {len(new_rows)} chargepoint sites to {SITES_CSV}")

print("Done.")
