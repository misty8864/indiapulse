from sqlalchemy import text
from src.db.connection import engine
from src.processing.transform import load_data
from loguru import logger








def create_table(engine):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS nse_bhavcopy (
        id SERIAL PRIMARY KEY,
        ticker_symbol TEXT,
        open_price FLOAT,
        close_price FLOAT,
        daily_return FLOAT
    );
    """

    with engine.connect() as conn:
        conn.execute(text(create_table_query))
        conn.commit()

    logger.success("Table created successfully.")





def insert_data(engine, final_df):
    final_df.to_sql(
        "nse_bhavcopy",
        engine,
        if_exists="append",
        index=False
    )

    logger.success("Data inserted successfully.")
    logger.info(f"Inserted {len(final_df)} rows into PostgreSQL.")


