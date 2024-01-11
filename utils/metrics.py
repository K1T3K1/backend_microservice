import math
import numpy as np
import pandas as pd

from database import get_influx_client


async def get_metric(companies_values: dict[str, float]) -> dict:
    result = {
        "ROI": None,
        "STDDEV": None,
        "INTERVAL": None,
        "SHARPE": None,
        "RECOMMENDATION": None,
    }
    companies = list(companies_values.keys())
    roi, company_df = await calculate_rois(companies)
    covariances = {(a, b): calculate_covariance(a, b, company_df) for idx_a, a in enumerate(companies) for b in
                   companies[idx_a + 1:]}

    investment_sum = sum([value for _, value in companies_values.items()])
    weights = {company: value / investment_sum for company, value in companies_values.items()}

    rois_small = [roi[symbol] * weights[symbol] for symbol in companies]
    result["ROI"] = sum(rois_small)
    stddev_base = [weights[a] ** 2 * company_df[a]['StdDev'].min() ** 2 for a in companies]
    stddev_base.extend([weights[a] * weights[b] * covariances[a, b] * 2 for a, b in covariances])
    result["STDDEV"] = math.sqrt(sum(stddev_base))
    stddev = result["STDDEV"]
    roi = result["ROI"]
    result["INTERVAL"] = (roi - stddev, roi + stddev)
    result["SHARPE"] = (roi - 0.02738) / stddev
    sharpe = result["SHARPE"]
    if sharpe < 0.01:
        result["RECOMMENDATION"] = "NOT RECOMMENDED"
    elif sharpe < 0.1:
        result["RECOMMENDATION"] = "SUB-OPTIMAL"
    elif 0.1 <= sharpe < 0.2:
        result["RECOMMENDATION"] = "RECOMMENDED"
    elif 0.2 < sharpe:
        result["RECOMMENDATION"] = "HIGHLY RECOMMENDED"

    return result


def calculate_covariance(company_a: str, company_b: str, company_df) -> float:
    if company_df[company_a].empty or company_df[company_b].empty:
        return
    a_df = company_df[company_a].dropna(how="any")
    b_df = company_df[company_b].dropna(how="any")
    return np.cov(a_df["DailyReturns"], b_df["DailyReturns"])[0][1]


async def calculate_rois(companies: list[str]) -> tuple[dict, dict]:
    roi = {symbol: 0 for symbol in companies}
    company_df = {}
    for symbol in companies:
        client = await get_influx_client()
        df = await client.query_data("3m", symbol)

        # df = query_data(symbol,
        #                 "-3mo")  # tutaj query do influxa musicie przerobić pod swój kod, powinien wracać dataframe z danymi pojedynczej firmy
        df = pd.DataFrame(df.groupby([df._time.dt.year, df._time.dt.month, df._time.dt.day])["ClosePrice"].mean())
        df["PreviousCloseMean"] = df.shift(1)
        df["DailyReturns"] = ((df["ClosePrice"] - df["PreviousCloseMean"]) / df["PreviousCloseMean"]) * 100
        df["StdDev"] = df["DailyReturns"].std()
        roi[symbol] = df["DailyReturns"].mean()
        company_df[symbol] = df
    return roi, company_df
