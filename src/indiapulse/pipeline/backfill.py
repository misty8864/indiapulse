from datetime import date, timedelta
from io import BytesIO
from zipfile import ZipFile, BadZipFile
import requests
from loguru import logger
from indiapulse.processing.transform import load_data
from indiapulse.db.load import create_table, insert_data
from sqlalchemy import create_engine


DB_URL = "postgresql+psycopg2://indiapulse_user:changeme_local@localhost:5432/indiapulse"
engine = create_engine(DB_URL)


def get_trading_dates(start_date: date, end_date: date) -> list:
    """Return all weekdays between start and end date."""
    dates = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # Mon-Fri only
            dates.append(current)
        current += timedelta(days=1)
    return dates


def download_and_load(target_date: date) -> int:
    date_str = target_date.strftime("%d%b%Y").upper()
    url = (
        f"https://nsearchives.nseindia.com/content/cm/"
        f"BhavCopy_NSE_CM_0_0_0_"
        f"{target_date.strftime('%Y%m%d')}_F_0000.csv.zip"
    )
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        with ZipFile(BytesIO(response.content)) as z:
            csv_name = z.namelist()[0]
            with z.open(csv_name) as f:
                df = load_data(f)

        rows = insert_data(engine, df)
        logger.success(f"{target_date} — inserted {rows} rows")
        return rows

    except Exception as e:
        logger.warning(f"{target_date} — skipped: {e}")
        return 0


def run_backfill(days: int = 60):
    create_table(engine)
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=days * 1.5)  # extra buffer for weekends
    trading_dates = get_trading_dates(start_date.date() if hasattr(start_date, 'date') else start_date, end_date)
    trading_dates = trading_dates[-days:]  # keep last N trading days

    logger.info(f"Backfilling {len(trading_dates)} trading days...")
    total = 0
    for d in trading_dates:
        rows = download_and_load(d)
        total += rows

    logger.success(f"Backfill complete. Total rows inserted: {total}")


if __name__ == "__main__":
    run_backfill(days=60)