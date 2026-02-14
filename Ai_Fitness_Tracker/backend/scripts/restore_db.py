import os
import shutil
import sys
from pathlib import Path

# Add parent directory to path to import settings
sys.path.append(str(Path(__file__).parent.parent))
from app.core.config import settings

def restore_sqlite(backup_file, db_path):
    if not os.path.exists(backup_file):
        print(f"Error: Backup file {backup_file} not found.")
        return False
    
    try:
        # Backup current DB before restoring just in case
        if os.path.exists(db_path):
            shutil.move(db_path, f"{db_path}.old")
            print(f"Moved current database to {db_path}.old")
            
        shutil.copy2(backup_file, db_path)
        print(f"Successfully restored SQLite database from {backup_file}")
        return True
    except Exception as e:
        print(f"Error during SQLite restore: {e}")
        # Try to recover if moved
        if os.path.exists(f"{db_path}.old"):
             shutil.move(f"{db_path}.old", db_path)
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python restore_db.py <backup_file_path>")
        return

    backup_file = Path(sys.argv[1])
    
    if settings.USE_POSTGRES:
        print("Postgres restore must be done manually using psql:")
        print(f"psql -U {settings.DATABASE_USERNAME} -d {settings.DATABASE_NAME} < {backup_file}")
    else:
        db_url = settings.get_database_url(is_async=False)
        if db_url.startswith("sqlite:///"):
            db_path = db_url.replace("sqlite:///", "")
            restore_sqlite(backup_file, db_path)
        else:
            print(f"Unsupported database URL for automatic restore: {db_url}")

if __name__ == "__main__":
    main()
