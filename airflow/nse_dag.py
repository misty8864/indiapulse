from datetime import datetime, timedelta
from pathlib import Path
import zipfile
import requests
import sys

sys.path.insert(0, "/opt/airflow/src")

from airflow import DAG
from airflow.operators.python import PythonOperator

DB_URL = "postgresql+psycopg2://indiapulse_user:changeme_local@host.docker.internal:5432/indiapulse"

default_args = {
    "owner": "indiapulse",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def download_bhavcopy(**context):
    date_str = context["ds_nodash"]  # e.g. 20241114
    url = (
        f"https://nsearchives.nseindia.com/content/cm/"
        f"BhavCopy_NSE_CM_0_0_0_{date_str}_F_0000.csv.zip"
    )
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    out_dir = Path("/tmp/nse")
    out_dir.mkdir(exist_ok=True)
    zip_path = out_dir / f"bhavcopy_{date_str}.zip"
    with open(zip_path, "wb") as f:
        f.write(response.content)


def extract_bhavcopy(**context):
    date_str = context["ds_nodash"]
    out_dir = Path("/tmp/nse")
    zip_path = out_dir / f"bhavcopy_{date_str}.zip"
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(out_dir)


def transform_and_load(**context):
    import sys
    sys.path.insert(0, "/opt/airflow/src")

    from pathlib import Path
    import pandas as pd
    from sqlalchemy import create_engine, text

    date_str = context["ds_nodash"]
    out_dir = Path("/tmp/nse")
    csv_path = out_dir / f"BhavCopy_NSE_CM_0_0_0_{date_str}_F_0000.csv"

    from indiapulse.processing.transform import load_data
    from indiapulse.db.load import create_table, insert_data

    # Direct DB URL — no .env needed inside container
    engine = create_engine(
        "postgresql+psycopg2://indiapulse_user:changeme_local@host.docker.internal:5432/indiapulse"
    )

    df = load_data(str(csv_path))
    create_table(engine)
    rows = insert_data(engine, df)
    print(f"Inserted {rows} rows for {date_str}")

with DAG(
    dag_id="nse_bhavcopy_pipeline",
    default_args=default_args,
    start_date=datetime(2024, 11, 14),
    schedule_interval="0 18 * * 1-5",
    catchup=False,
    tags=["indiapulse", "ingestion"],
) as dag:

    t1 = PythonOperator(task_id="download", python_callable=download_bhavcopy)
    t2 = PythonOperator(task_id="extract", python_callable=extract_bhavcopy)
    t3 = PythonOperator(task_id="transform_and_load", python_callable=transform_and_load)

    t1 >> t2 >> t3