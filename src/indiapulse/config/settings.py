import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql+psycopg2://indiapulse_user:changeme_local@localhost:5432/indiapulse"

POSTGRES_USER = os.getenv("POSTGRES_USER", "indiapulse_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "changeme_local")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "indiapulse")