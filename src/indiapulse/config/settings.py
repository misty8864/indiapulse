import os
from dotenv import load_dotenv

# Load from .env only if it exists (for local dev)
# On Railway, this will be skipped since .env doesn't exist
if os.path.exists(".env"):
    load_dotenv()

# Try to get DATABASE_URL directly first (Railway environment variable)
DATABASE_URL = os.getenv("DATABASE_URL")

# If DATABASE_URL not available, build it from individual components (local dev)
if not DATABASE_URL:
    POSTGRES_USER = os.getenv("POSTGRES_USER", "indiapulse_user")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "changeme_local")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "indiapulse")
    
    DATABASE_URL = (
        f"postgresql+psycopg2://"
        f"{POSTGRES_USER}:"
        f"{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:"
        f"{POSTGRES_PORT}/"
        f"{POSTGRES_DB}"
    )

# Export individual components for backward compatibility (if needed)
POSTGRES_USER = os.getenv("POSTGRES_USER", "indiapulse_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "changeme_local")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "indiapulse")