from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
from pathlib import Path
import zipfile
import pandas as pd
from sqlalchemy import create_engine, text

DB_URL = "postgresql+psycopg2://indiapulse_user:changeme_local@postgres:5432/indiapulse"

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def download_bhavcopy(**context):
    date = "20241114"  # hardcoded for testing
    url = f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{date}_F_0000.csv.zip"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    out_dir = Path("/tmp/nse")
    out_dir.mkdir(exist_ok=True)
    zip_path = out_dir / f"bhavcopy_{date}.zip"
    with open(zip_path, "wb") as f:
        f.write(response.content)

def extract_bhavcopy(**context):
    date = "20241114"  # hardcoded for testing
    out_dir = Path("/tmp/nse")
    zip_path = out_dir / f"bhavcopy_{date}.zip"
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(out_dir)

def insert_bhavcopy(**context):
    date = "20241114"  # hardcoded for testing
    out_dir = Path("/tmp/nse")
    csv_path = out_dir / f"BhavCopy_NSE_CM_0_0_0_{date}_F_0000.csv"
    df = pd.read_csv(csv_path)
    df["daily_return"] = (df["ClsPric"] - df["OpnPric"]) / df["OpnPric"]
    final_df = df[["TckrSymb", "OpnPric", "ClsPric", "daily_return"]]
    final_df.columns = ["ticker_symbol", "open_price", "close_price", "daily_return"]
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS nse_bhavcopy (
                id SERIAL PRIMARY KEY,
                ticker_symbol TEXT,
                open_price FLOAT,
                close_price FLOAT,
                daily_return FLOAT
            )
        """))
        conn.commit()
    final_df.to_sql("nse_bhavcopy", engine, if_exists="append", index=False)

with DAG(
    dag_id="nse_bhavcopy_pipeline",
    default_args=default_args,
    start_date=datetime(2024, 11, 14),
    schedule_interval="0 18 * * 1-5",
    catchup=False,
) as dag:

    t1 = PythonOperator(task_id="download", python_callable=download_bhavcopy)
    t2 = PythonOperator(task_id="extract", python_callable=extract_bhavcopy)
    t3 = PythonOperator(task_id="insert", python_callable=insert_bhavcopy)

    t1 >> t2 >> t3