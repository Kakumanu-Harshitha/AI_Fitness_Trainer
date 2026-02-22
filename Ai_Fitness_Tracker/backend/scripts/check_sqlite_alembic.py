import sqlite3
import os

# Check root fitness_v3.db
db_path = "fitness_v3.db"
print(f"Checking DB at: {db_path}")

if not os.path.exists(db_path):
    print(f"DB file not found at {db_path}")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM alembic_version')
        print(f"Current Alembic Revision in root DB: {cursor.fetchall()}")
        conn.close()
    except Exception as e:
        print(f"Error checking alembic version in root DB: {e}")

# Check backend/fitness_v3.db
db_path_backend = os.path.join("backend", "fitness_v3.db")
print(f"Checking DB at: {db_path_backend}")

if not os.path.exists(db_path_backend):
    print(f"DB file not found at {db_path_backend}")
else:
    try:
        conn = sqlite3.connect(db_path_backend)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM alembic_version')
        print(f"Current Alembic Revision in backend DB: {cursor.fetchall()}")
        conn.close()
    except Exception as e:
        print(f"Error checking alembic version in backend DB: {e}")
