from sqlalchemy import create_engine
from indiapulse.config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL)