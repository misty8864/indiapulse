from loguru import logger
import argparse

from indiapulse.db.connection import engine
from indiapulse.db.load import create_table, insert_data
from indiapulse.processing.transform import load_data


def main(path: str):
    logger.info("Starting IndiaPulse pipeline...")

    create_table(engine)

    final_df = load_data(path)
    logger.info(f"Transformed {len(final_df)} rows.")

    rows = insert_data(engine, final_df)
    logger.info(f"Pipeline complete. {rows} rows inserted.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--path",
        required=True,
        help="Path to NSE bhavcopy CSV file"
    )

    args = parser.parse_args()

    main(args.path)