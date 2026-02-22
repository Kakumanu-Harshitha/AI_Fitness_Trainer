import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

# Credentials from .env
user = "postgres"
password = "Kharshitha123"
host = "localhost"
port = "5432"
dbname = "fitness_tracker"

def create_database():
    try:
        # Connect to default 'postgres' database
        con = psycopg2.connect(dbname='postgres', user=user, host=host, password=password, port=port)
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        
        # Check if database exists
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'")
        exists = cur.fetchone()
        
        if not exists:
            print(f"Creating database {dbname}...")
            cur.execute(f"CREATE DATABASE {dbname}")
            print(f"Database {dbname} created successfully!")
        else:
            print(f"Database {dbname} already exists.")
            
        cur.close()
        con.close()
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

if __name__ == "__main__":
    create_database()
