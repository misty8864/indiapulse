import pandas as pd


SECTOR_MAP = {
    "INFY": "IT", "TCS": "IT", "WIPRO": "IT", "HCLTECH": "IT",
    "HDFCBANK": "Banking", "ICICIBANK": "Banking", "SBIN": "Banking",
    "RELIANCE": "Energy", "ONGC": "Energy", "NTPC": "Energy",
    "SUNPHARMA": "Pharma", "DRREDDY": "Pharma", "CIPLA": "Pharma",
    "TATAMOTORS": "Auto", "MARUTI": "Auto",
}


def compute_daily_return(df: pd.DataFrame) -> pd.Series:
    open_safe = df["open_price"].replace(0, float("nan"))
    return (df["close_price"] - df["open_price"]) / open_safe


def load_data(path: str) -> pd.DataFrame:
    raw_df = pd.read_csv(path)

    df = pd.DataFrame()
    df["trade_date"]    = pd.to_datetime(raw_df["TradDt"]).dt.date
    df["ticker_symbol"] = raw_df["TckrSymb"].str.strip()
    df["series"]        = raw_df["SctySrs"].str.strip()
    df["open_price"]    = pd.to_numeric(raw_df["OpnPric"], errors="coerce")
    df["close_price"]   = pd.to_numeric(raw_df["ClsPric"], errors="coerce")
    df["volume"]        = pd.to_numeric(raw_df["TtlTradgVol"], errors="coerce")
    df["sector"]        = df["ticker_symbol"].map(SECTOR_MAP).fillna("Other")
    df["daily_return"]  = compute_daily_return(df)

    # Keep only EQ series
    df = df[df["series"] == "EQ"].copy()
    df = df.dropna(subset=["close_price"])

    return df[["trade_date", "ticker_symbol", "series", "sector",
               "open_price", "close_price", "volume", "daily_return"]]