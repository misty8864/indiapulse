import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:"
    f"{os.getenv('POSTGRES_PORT')}/"
    f"{os.getenv('POSTGRES_DB')}"
)

engine = create_engine(DATABASE_URL)


def create_table():
    query = """
    CREATE TABLE IF NOT EXISTS nse_bhavcopy (
        id SERIAL PRIMARY KEY,
        ticker_symbol TEXT,
        open_price FLOAT,
        close_price FLOAT,
        daily_return FLOAT
    );
    """

    with engine.connect() as conn:
        conn.execute(text(query))
        conn.commit()


def load_data():
    df = pd.read_csv(
        "data/nse_temp/BhavCopy_NSE_CM_0_0_0_20241114_F_0000.csv"
    )

    df["daily_return"] = (df["ClsPric"] - df["OpnPric"]) / df["OpnPric"]

    final_df = df[[
        "TckrSymb",
        "OpnPric",
        "ClsPric",
        "daily_return"
    ]]

    final_df.columns = [
        "ticker_symbol",
        "open_price",
        "close_price",
        "daily_return"
    ]

    return final_df


def insert_data(df):
    df.to_sql(
        "nse_bhavcopy",
        engine,
        if_exists="append",
        index=False
    )


def main():
    create_table()
    df = load_data()
    insert_data(df)

    print("Pipeline executed successfully 🚀")


if __name__ == "__main__":
    main()