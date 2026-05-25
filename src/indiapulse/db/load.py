from sqlalchemy import text
from loguru import logger


def create_table(engine) -> None:
    create_table_query = """
    CREATE TABLE IF NOT EXISTS nse_bhavcopy (
        id SERIAL PRIMARY KEY,
        trade_date DATE,
        ticker_symbol TEXT,
        series TEXT,
        sector TEXT,
        open_price FLOAT,
        close_price FLOAT,
        volume BIGINT,
        daily_return FLOAT,
        UNIQUE (trade_date, ticker_symbol)
    );
    """
    with engine.connect() as conn:
        conn.execute(text(create_table_query))
        conn.commit()
    logger.success("Table created/verified successfully.")


def insert_data(engine, final_df) -> int:
    with engine.connect() as conn:
        # Drop existing rows for this trade_date to avoid duplicates
        dates = final_df["trade_date"].unique().tolist()
        conn.execute(
            text("DELETE FROM nse_bhavcopy WHERE trade_date = ANY(:dates)"),
            {"dates": dates}
        )
        final_df.to_sql(
            "nse_bhavcopy",
            conn,
            if_exists="append",
            index=False,
            chunksize=500
        )
        conn.commit()
    rows = len(final_df)
    logger.success(f"Inserted {rows} rows.")
    return rows