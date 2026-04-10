#!/usr/bin/env python3
"""
CLI tool for managing Firestore database
"""

import logging
import sys
from pathlib import Path

import click
import colorlog

from lib.firestore_client import FirestoreClient
from lib.operations import DatabaseOperations


# Setup colored logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))

logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, verbose):
    """Database management CLI for EU E-Mobility Investment Map"""
    if verbose:
        logger.setLevel(logging.DEBUG)
    
    # Store client in context
    ctx.ensure_object(dict)


@cli.command()
@click.option('--countries', '-c', type=click.Path(exists=True), help='Path to countries CSV/JSON file')
@click.option('--sites', '-s', type=click.Path(exists=True), help='Path to sites CSV/JSON file')
@click.option('--dry-run', is_flag=True, help='Preview changes without writing to database')
@click.pass_context
def seed(ctx, countries, sites, dry_run):
    """Seed database with initial data (replaces all existing data)"""
    
    if not countries and not sites:
        click.echo("❌ Error: Must specify at least --countries or --sites")
        sys.exit(1)
    
    if dry_run:
        click.echo("🔍 DRY RUN MODE - No changes will be made")
    
    try:
        client = FirestoreClient()
        ops = DatabaseOperations(client)
        
        click.echo("\n🔥 Seeding Database")
        click.echo("=" * 50)
        
        results = ops.seed_database(
            countries_file=countries,
            sites_file=sites,
            dry_run=dry_run
        )
        
        click.echo("\n✅ Seeding Complete!")
        click.echo(f"   Countries: {results['countries']}")
        click.echo(f"   Sites: {results['sites']}")
        if results['errors'] > 0:
            click.echo(f"   ⚠️  Errors: {results['errors']}")
        click.echo("=" * 50 + "\n")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        if ctx.obj.get('verbose'):
            raise
        sys.exit(1)


@cli.command()
@click.argument('collection', type=click.Choice(['countries', 'sites']))
@click.option('--file', '-f', 'file_path', required=True, type=click.Path(exists=True), help='Path to data file')
@click.option('--mode', '-m', type=click.Choice(['merge', 'sync', 'add-new', 'replace']), default='merge', 
              help='Update mode (merge=update+add, sync=update+add+delete, add-new=only add, replace=delete all+add)')
@click.option('--dry-run', is_flag=True, help='Preview changes without writing')
@click.pass_context
def update(ctx, collection, file_path, mode, dry_run):
    """Update a collection with smart merging strategies"""
    
    if dry_run:
        click.echo("🔍 DRY RUN MODE - No changes will be made")
    
    try:
        client = FirestoreClient()
        ops = DatabaseOperations(client)
        
        click.echo(f"\n🔄 Updating {collection}")
        click.echo("=" * 50)
        click.echo(f"Mode: {mode}")
        click.echo(f"File: {file_path}")
        
        results = ops.update_collection(
            collection=collection,
            file_path=file_path,
            mode=mode,
            dry_run=dry_run
        )
        
        click.echo("\n✅ Update Complete!")
        if results['added'] > 0:
            click.echo(f"   ✚ Added: {results['added']}")
        if results['updated'] > 0:
            click.echo(f"   ↻ Updated: {results['updated']}")
        if results['deleted'] > 0:
            click.echo(f"   ✖ Deleted: {results['deleted']}")
        if results['errors'] > 0:
            click.echo(f"   ⚠️  Errors: {results['errors']}")
        click.echo("=" * 50 + "\n")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        if ctx.obj.get('verbose'):
            raise
        sys.exit(1)


@cli.command()
@click.argument('collection', type=click.Choice(['countries', 'sites', 'all']))
@click.option('--format', '-f', type=click.Choice(['csv', 'json']), default='csv', help='Output format')
@click.option('--output', '-o', required=True, type=click.Path(), help='Output file path (or directory for "all")')
@click.pass_context
def export(ctx, collection, format, output):
    """Export collection(s) to file"""
    
    try:
        client = FirestoreClient()
        ops = DatabaseOperations(client)
        
        click.echo(f"\n📤 Exporting {collection}")
        click.echo("=" * 50)
        
        if collection == 'all':
            # Export all collections
            output_dir = Path(output)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            for coll in ['countries', 'sites']:
                output_file = output_dir / f"{coll}.{format}"
                count = ops.export_collection(coll, str(output_file), format=format)
                click.echo(f"   ✓ {coll}: {count} records → {output_file}")
        else:
            # Export single collection
            count = ops.export_collection(collection, output, format=format)
            click.echo(f"   ✓ Exported {count} records to {output}")
        
        click.echo("=" * 50 + "\n")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        if ctx.obj.get('verbose'):
            raise
        sys.exit(1)


@cli.command()
@click.argument('collection', type=click.Choice(['countries', 'sites']))
@click.option('--confirm', is_flag=True, help='Confirm deletion (required)')
@click.pass_context
def clear(ctx, collection, confirm):
    """Clear all documents from a collection"""
    
    if not confirm:
        click.echo("❌ Error: Must use --confirm flag to proceed")
        click.echo("   This operation will DELETE ALL documents!")
        sys.exit(1)
    
    # Double confirmation
    click.echo(f"\n⚠️  WARNING: This will DELETE ALL documents in '{collection}'")
    if not click.confirm("Are you absolutely sure?"):
        click.echo("Aborted.")
        return
    
    try:
        client = FirestoreClient()
        ops = DatabaseOperations(client)
        
        click.echo(f"\n🗑️  Clearing {collection}")
        click.echo("=" * 50)
        
        count = ops.clear_collection(collection, confirm=True)
        
        click.echo(f"\n✅ Cleared {count} documents from '{collection}'")
        click.echo("=" * 50 + "\n")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        if ctx.obj.get('verbose'):
            raise
        sys.exit(1)


@cli.command()
@click.option('--file', '-f', 'file_path', required=True, type=click.Path(exists=True), help='Path to data file')
@click.option('--schema', '-s', type=click.Choice(['country', 'site']), required=True, help='Data schema to validate against')
@click.pass_context
def validate(ctx, file_path, schema):
    """Validate data file without uploading"""
    
    try:
        from lib.csv_parser import CSVParser
        from lib.validators import validate_batch_countries, validate_batch_sites
        
        click.echo(f"\n✓ Validating {file_path}")
        click.echo("=" * 50)
        
        data = CSVParser.auto_read(file_path)
        click.echo(f"Read {len(data)} records")
        
        if schema == 'country':
            valid, invalid = validate_batch_countries(data)
        else:
            valid, invalid = validate_batch_sites(data)
        
        if invalid:
            click.echo(f"\n❌ Found {len(invalid)} invalid records:\n")
            for err in invalid[:10]:  # Show first 10 errors
                click.echo(f"   Row {err['row']}: {err['error']}")
            if len(invalid) > 10:
                click.echo(f"   ... and {len(invalid) - 10} more errors")
        
        click.echo(f"\n✅ Valid records: {len(valid)}")
        click.echo(f"❌ Invalid records: {len(invalid)}")
        
        if invalid:
            click.echo("\n⚠️  Fix validation errors before uploading")
            sys.exit(1)
        else:
            click.echo("\n✅ All records are valid!")
        
        click.echo("=" * 50 + "\n")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        if ctx.obj.get('verbose'):
            raise
        sys.exit(1)


@cli.command()
@click.pass_context
def info(ctx):
    """Show database connection info"""
    
    try:
        client = FirestoreClient()
        
        click.echo("\n📊 Database Information")
        click.echo("=" * 50)
        
        for collection in ['countries', 'sites']:
            count = client.get_document_count(collection)
            click.echo(f"   {collection}: {count} documents")
        
        click.echo("=" * 50 + "\n")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        if ctx.obj.get('verbose'):
            raise
        sys.exit(1)


@cli.command('sync-battery')
@click.option('--mode', '-m',
              type=click.Choice(['merge', 'replace', 'add-new']),
              default='merge',
              help='Sync mode: merge=update+add, replace=delete all battery+re-add, add-new=only add new')
@click.option('--dry-run', is_flag=True, help='Preview changes without writing to Firestore')
@click.option('--config', 'sql_config_path', default=None, type=click.Path(),
              help='Path to sql-config.json (default: config/sql-config.json)')
@click.pass_context
def sync_battery(ctx, mode, dry_run, sql_config_path):
    """Sync battery manufacturing projects from Cloud SQL (MySQL) → Firestore"""

    if dry_run:
        click.echo("🔍 DRY RUN MODE - No changes will be made")

    try:
        from lib.sql_client import CloudSQLClient
        from scripts.sync_from_sql import sync_battery_to_firestore

        click.echo("\n🔋 Battery Sync: Cloud SQL → Firestore")
        click.echo("=" * 50)
        click.echo(f"Mode: {mode}")

        # Connect to Cloud SQL
        click.echo("🔌 Connecting to Cloud SQL...")
        sql_client = CloudSQLClient(config_path=sql_config_path)
        sql_client.connect()

        # Connect to Firestore
        firestore_client = FirestoreClient()

        results = sync_battery_to_firestore(
            sql_client=sql_client,
            firestore_client=firestore_client,
            mode=mode,
            dry_run=dry_run,
        )

        sql_client.close()

        click.echo("\n✅ Sync Complete!")
        if results['added'] > 0:
            click.echo(f"   ✚ Added:   {results['added']} battery sites")
        if results['updated'] > 0:
            click.echo(f"   ↻ Updated: {results['updated']} battery sites")
        if results['deleted'] > 0:
            click.echo(f"   ✖ Deleted: {results['deleted']} battery sites")
        if results['skipped'] > 0:
            click.echo(f"   ⏭  Skipped: {results['skipped']} (already exist)")
        click.echo("=" * 50 + "\n")

    except FileNotFoundError as e:
        click.echo(f"\n❌ Config error: {e}", err=True)
        click.echo("\n💡 Make sure you have:")
        click.echo("   1. database/config/sql-config.json  (connection details)")
        click.echo("   2. database/config/sql-credentials.json  (service account key)")
        sys.exit(1)
    except ImportError as e:
        click.echo(f"\n❌ Missing dependency: {e}", err=True)
        click.echo("\n💡 Run: pip install cloud-sql-python-connector[pymysql] pymysql google-auth")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        if ctx.obj.get('verbose'):
            raise
        sys.exit(1)


if __name__ == '__main__':
    cli(obj={})
