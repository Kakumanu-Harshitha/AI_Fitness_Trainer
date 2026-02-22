import sys
import os

# Add the parent directory to sys.path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.app.core.config import settings

print(f"USE_POSTGRES: {settings.USE_POSTGRES}")
print(f"DATABASE_URL (raw): {settings.DATABASE_URL}")
print(f"Computed DB URL (async): {settings.get_database_url(is_async=True)}")
print(f"Computed DB URL (sync): {settings.get_database_url(is_async=False)}")
