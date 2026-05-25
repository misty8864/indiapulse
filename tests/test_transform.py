import pandas as pd
import pytest
from indiapulse.processing.transform import compute_daily_return, load_data


class TestComputeDailyReturn:

    def test_positive_return(self):
        df = pd.DataFrame({"open_price": [100.0], "close_price": [110.0]})
        result = compute_daily_return(df)
        assert abs(result.iloc[0] - 0.10) < 0.001

    def test_negative_return(self):
        df = pd.DataFrame({"open_price": [200.0], "close_price": [190.0]})
        result = compute_daily_return(df)
        assert abs(result.iloc[0] - (-0.05)) < 0.001

    def test_zero_open_returns_nan(self):
        df = pd.DataFrame({"open_price": [0.0], "close_price": [100.0]})
        result = compute_daily_return(df)
        assert pd.isna(result.iloc[0])


class TestLoadData:

    def test_returns_dataframe(self):
        path = "data/nse_temp/BhavCopy_NSE_CM_0_0_0_20241114_F_0000.csv"
        df = load_data(path)
        assert isinstance(df, pd.DataFrame)

    def test_correct_columns(self):
        path = "data/nse_temp/BhavCopy_NSE_CM_0_0_0_20241114_F_0000.csv"
        df = load_data(path)
        expected = {"trade_date", "ticker_symbol", "series",
                    "sector", "open_price", "close_price",
                    "volume", "daily_return"}
        assert expected.issubset(set(df.columns))

    def test_only_eq_series(self):
        path = "data/nse_temp/BhavCopy_NSE_CM_0_0_0_20241114_F_0000.csv"
        df = load_data(path)
        assert df["series"].unique().tolist() == ["EQ"]

    def test_row_count_reasonable(self):
        path = "data/nse_temp/BhavCopy_NSE_CM_0_0_0_20241114_F_0000.csv"
        df = load_data(path)
        assert len(df) > 1000