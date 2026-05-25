from loguru import logger

from indiapulse.db.connection import engine
from indiapulse.db.load import create_table, insert_data
from indiapulse.processing.transform import load_data


def main():
    path = "data/nse_temp/BhavCopy_NSE_CM_0_0_0_20241114_F_0000.csv"

    logger.info("Starting IndiaPulse pipeline...")

    create_table(engine)

    final_df = load_data(path)
    logger.info(f"Transformed {len(final_df)} rows.")

    rows = insert_data(engine, final_df)
    logger.info(f"Pipeline complete. {rows} rows inserted.")


if __name__ == "__main__":
    main()