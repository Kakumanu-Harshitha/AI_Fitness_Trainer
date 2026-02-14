import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    host = os.getenv("DATABASE_HOSTNAME", "localhost")
    port = "5433" # Explicitly trying port 5433 from logs
    user = os.getenv("DATABASE_USERNAME", "postgres")
    password = os.getenv("DATABASE_PASSWORD", "password")
    dbname = os.getenv("DATABASE_NAME", "fitness_db")

    try:
        # Connect to default postgres database to create the new one
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database {dbname}...")
            cursor.execute(f"CREATE DATABASE {dbname}")
            print(f"Database {dbname} created successfully!")
        else:
            print(f"Database {dbname} already exists.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    create_database()
