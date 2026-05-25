from datetime import date
from pathlib import Path

import requests
from loguru import logger


def get_bhavcopy_date():
    return date(2024, 11, 14)


def build_bhavcopy_url(bhavcopy_date: date) -> str:
    formatted_date = bhavcopy_date.strftime("%Y%m%d")

    url = (
        f"https://nsearchives.nseindia.com/"
        f"content/cm/BhavCopy_NSE_CM_0_0_0_{formatted_date}_F_0000.csv.zip"
    )

    return url


def main():
    bhavcopy_date = get_bhavcopy_date()

    logger.info(f"Fetching NSE bhavcopy for: {bhavcopy_date}")

    url = build_bhavcopy_url(bhavcopy_date)

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)

    filename = url.rsplit("/", 1)[-1]
    out_path = out_dir / filename

    with open(out_path, "wb") as f:
        f.write(response.content)

    logger.success(f"Downloaded to {out_path}")


if __name__ == "__main__":
    main()