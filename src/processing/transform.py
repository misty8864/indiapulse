import pandas as pd


def load_data(path: str):
    raw_df = pd.read_csv(path)

    raw_df["daily_return"] = (
        (raw_df["ClsPric"] - raw_df["OpnPric"]) / raw_df["OpnPric"]
    )

    final_df = raw_df[[
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