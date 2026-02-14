import os
import shutil
import datetime
import subprocess
from pathlib import Path
import sys

# Add parent directory to path to import settings
sys.path.append(str(Path(__file__).parent.parent))
from app.core.config import settings

def backup_sqlite(db_path, backup_dir):
    if not os.path.exists(db_path):
        print(f"Error: Database file {db_path} not found.")
        return False
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"fitness_backup_{timestamp}.db"
    
    try:
        shutil.copy2(db_path, backup_file)
        print(f"Successfully backed up SQLite database to {backup_file}")
        return True
    except Exception as e:
        print(f"Error during SQLite backup: {e}")
        return False

def backup_postgres(backup_dir):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"fitness_backup_{timestamp}.sql"
    
    # pg_dump -U username -h hostname -p port dbname > backup_file
    env = os.environ.copy()
    env["PGPASSWORD"] = settings.DATABASE_PASSWORD
    
    command = [
        "pg_dump",
        "-U", settings.DATABASE_USERNAME,
        "-h", settings.DATABASE_HOSTNAME,
        "-p", str(settings.DATABASE_PORT),
        settings.DATABASE_NAME
    ]
    
    try:
        with open(backup_file, "w") as f:
            subprocess.run(command, stdout=f, env=env, check=True)
        print(f"Successfully backed up Postgres database to {backup_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during Postgres backup: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during Postgres backup: {e}")
        return False

def main():
    backup_dir = Path(__file__).parent.parent.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    print(f"Starting database backup... (Target dir: {backup_dir})")
    
    if settings.USE_POSTGRES:
        success = backup_postgres(backup_dir)
    else:
        # Default to SQLite
        db_url = settings.get_database_url(is_async=False)
        if db_url.startswith("sqlite:///"):
            db_path = db_url.replace("sqlite:///", "")
            success = backup_sqlite(db_path, backup_dir)
        else:
            print(f"Unsupported database URL for automatic backup: {db_url}")
            success = False
    
    if success:
        # Keep only last 7 backups
        backups = sorted(list(backup_dir.glob("fitness_backup_*")), key=os.path.getmtime)
        if len(backups) > 7:
            for old_backup in backups[:-7]:
                old_backup.unlink()
                print(f"Removed old backup: {old_backup}")

if __name__ == "__main__":
    main()
