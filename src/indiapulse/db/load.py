from sqlalchemy import text
from loguru import logger


CREATE_TABLE_QUERY = """
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


def create_table(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(CREATE_TABLE_QUERY))
    logger.success("Table created/verified successfully.")


def insert_data(engine, final_df) -> int:
    dates = final_df["trade_date"].unique().tolist()
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM nse_bhavcopy WHERE trade_date = ANY(:dates)"),
            {"dates": dates}
        )
    final_df.to_sql(
        "nse_bhavcopy",
        engine,
        if_exists="append",
        index=False,
        chunksize=500
    )
    rows = len(final_df)
    logger.success(f"Inserted {rows} rows.")
    return rows