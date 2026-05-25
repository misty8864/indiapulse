import io
import pandas as pd
from indiapulse.processing.transform import compute_daily_return, load_data


SAMPLE_CSV = """TckrSymb,OpnPric,HghPric,LwPric,ClsPric,TtlTradgVol,TradDt,SctySrs
INFY,1500.0,1520.0,1490.0,1510.0,1000000,2024-11-14,EQ
TCS,3500.0,3550.0,3480.0,3520.0,500000,2024-11-14,EQ
SBIN,600.0,610.0,595.0,605.0,2000000,2024-11-14,EQ
RELIANCE,2800.0,2850.0,2780.0,2820.0,1500000,2024-11-14,BE
"""


def get_sample_df():
    return load_data(io.StringIO(SAMPLE_CSV))


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
        df = get_sample_df()
        assert isinstance(df, pd.DataFrame)

    def test_correct_columns(self):
        df = get_sample_df()
        expected = {"trade_date", "ticker_symbol", "series",
                    "sector", "open_price", "close_price",
                    "volume", "daily_return"}
        assert expected.issubset(set(df.columns))

    def test_only_eq_series(self):
        df = get_sample_df()
        assert all(df["series"] == "EQ")

    def test_row_count_excludes_non_eq(self):
        df = get_sample_df()
        assert len(df) == 3