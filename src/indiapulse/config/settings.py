# ✅ NEW: Try DATABASE_URL first (Railway environment variable)
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ NEW: Only build from components if DATABASE_URL not available
if not DATABASE_URL:
    # Build it locally...