from src.db.load import create_table, insert_data
from src.db.connection import engine
from src.processing.transform import load_data


def main():
    path = "data/nse_temp/BhavCopy_NSE_CM_0_0_0_20241114_F_0000.csv"

    create_table(engine)

    final_df = load_data(path)

    insert_data(engine, final_df)


if __name__ == "__main__":
    main()