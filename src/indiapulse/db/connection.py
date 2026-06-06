from sqlalchemy import create_engine
from src.config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL)