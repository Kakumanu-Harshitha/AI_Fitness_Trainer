
import sqlite3
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from .env
DB_NAME = os.getenv("DATABASE_NAME", "fitness")
DB_USER = os.getenv("DATABASE_USERNAME", "postgres")
DB_PASS = os.getenv("DATABASE_PASSWORD", "Kharshitha123")
DB_HOST = os.getenv("DATABASE_HOSTNAME", "localhost")
DB_PORT = os.getenv("DATABASE_PORT", "5432")
SQLITE_DB = "fitness.db"

def migrate():
    if not os.path.exists(SQLITE_DB):
        print(f"Error: {SQLITE_DB} not found.")
        return

    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()

        # Connect to Postgres
        pg_conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        pg_cursor = pg_conn.cursor()
        print(f"Connected to Postgres database: {DB_NAME}")

        # Get all tables from SQLite
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row['name'] for row in sqlite_cursor.fetchall()]

        for table in tables:
            if table == 'alembic_version':
                print(f"Skipping table: {table}")
                continue
            print(f"Migrating table: {table}...")
            
            # Fetch data from SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"  Table {table} is empty. Skipping.")
                continue

            # Get columns
            columns = rows[0].keys()
            
            # Prepare Postgres insert statement
            # We use ON CONFLICT DO NOTHING to avoid duplicate errors if some data exists
            insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) ON CONFLICT DO NOTHING").format(
                sql.Identifier(table),
                sql.SQL(', ').join(map(sql.Identifier, columns)),
                sql.SQL(', ').join(sql.Placeholder() * len(columns))
            )

            # Insert data into Postgres
            for row in rows:
                pg_cursor.execute(insert_query, list(row))
            
            pg_conn.commit()
            print(f"  Successfully migrated {len(rows)} rows to {table}.")

        print("\nMigration completed successfully!")

    except Exception as e:
        print(f"An error occurred during migration: {e}")
        if 'pg_conn' in locals():
            pg_conn.rollback()
    finally:
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    migrate()
