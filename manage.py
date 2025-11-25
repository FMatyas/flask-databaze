#!/usr/bin/env python3
import json
import os
import sys
from flask.cli import with_appcontext
import click
from app import app, db
from alembic import command
from alembic.config import Config

ALEMBIC_INI = os.path.join(os.path.dirname(__file__), 'alembic.ini')

@click.group()
def cli():
    pass

@cli.command('init-db')
@with_appcontext
def init_db():
    """Create database and tables from models."""
    db.create_all()
    click.echo('Database initialized')

@cli.command('migrate')
@click.argument('message', default='auto migration')
@with_appcontext
def migrate(message):
    """Create an Alembic migration (autogenerate)."""
    cfg = Config(ALEMBIC_INI)
    command.revision(cfg, message=message, autogenerate=True)
    click.echo('Revision created')

@cli.command('upgrade')
@click.argument('revision', default='head')
@with_appcontext
def upgrade(revision):
    """Apply Alembic migrations."""
    cfg = Config(ALEMBIC_INI)
    command.upgrade(cfg, revision)
    click.echo('Database upgraded to %s' % revision)

@cli.command('export-db')
@click.argument('path', default='dump.json')
@with_appcontext
def export_db(path):
    """Export products to JSON file. Detect available columns to avoid SQL errors."""
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), 'products.db')
    if not os.path.exists(db_path):
        click.echo('Database file not found: %s' % db_path)
        return
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(product)")
    cols = [r['name'] for r in cur.fetchall()]
    want = ['id','name','price','description','dph']
    select_cols = [c for c in want if c in cols]
    if not select_cols:
        click.echo('No product columns found to export')
        return
    q = 'SELECT ' + ','.join(select_cols) + ' FROM product'
    items = []
    try:
        for row in cur.execute(q):
            item = {col: row[col] if col in row.keys() else None for col in select_cols}
            # ensure all wanted keys exist
            if 'dph' not in item:
                item['dph'] = 15
            if 'description' not in item:
                item['description'] = None
            items.append(item)
    except Exception as e:
        click.echo('Error exporting: %s' % e)
        conn.close()
        return
    conn.close()
    with open(path,'w',encoding='utf-8') as f:
        json.dump(items,f,ensure_ascii=False,indent=2)
    click.echo('Exported %d products to %s' % (len(items), path))

@cli.command('import-db')
@click.argument('path')
@with_appcontext
def import_db(path):
    """Import products from JSON file. Inserts only available columns in DB."""
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), 'products.db')
    if not os.path.exists(path):
        click.echo('Import file not found: %s' % path)
        return
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(product)")
    cols = [r[1] for r in cur.fetchall()]
    # determine which columns we can insert (exclude id if it's PK autoinc)
    insert_cols = [c for c in ['name','price','description','dph'] if c in cols]
    if not insert_cols:
        click.echo('No target columns in product table to import into')
        conn.close()
        return
    with open(path,'r',encoding='utf-8') as f:
        items = json.load(f)
    count = 0
    for it in items:
        values = [it.get(c, 15 if c=='dph' else None) for c in insert_cols]
        placeholders = ','.join(['?']*len(insert_cols))
        sql = f"INSERT INTO product ({','.join(insert_cols)}) VALUES ({placeholders})"
        cur.execute(sql, values)
        count += 1
    conn.commit()
    conn.close()
    click.echo('Imported %d products from %s' % (count, path))

if __name__ == '__main__':
    cli()
