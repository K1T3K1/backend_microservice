import datetime
import logging
import os
from typing import Optional
from datetime import datetime, timedelta

import influxdb_client
from dotenv import load_dotenv
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from pandas import DataFrame
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

load_dotenv()

database_url = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# influx_client = influxdb_client.InfluxDBClient(url=os.getenv('INFUX_URL'), token=os.getenv('INFUX_TOKEN'),
#                                                org=os.getenv('INFUX_ORG'), timeout=1000000)


class InfluxClient:
    _client: InfluxDBClientAsync
    _bucket: str

    @classmethod
    async def get_uploader(cls, url: str, token: str, org: str, bucket: str):
        self = cls()
        self._client = InfluxDBClientAsync(url, token, org, enable_gzip=True)
        self._bucket = bucket
        return self

    def format_date(self, date: datetime) -> str:
        return date.strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_dates_from_now(self, range: str) -> tuple[datetime, datetime]:
        now = datetime.utcnow()
        # parse range
        # check if last char is d, m, y
        # if not, raise error
        # if so, get the number

        if range[-1] not in ["d", "m", "y", "h"]:
            raise ValueError("Invalid range")

        try:
            num = int(range[:-1])
        except ValueError:
            raise ValueError("Invalid range")

        if range[-1] == "d":
            start = now - timedelta(days=num)
            return start, now

        if range[-1] == "m":
            start = now - timedelta(days=num * 30)
            return start, now

        if range[-1] == "y":
            start = now - timedelta(days=num * 365)
            return start, now

        if range[-1] == "h":
            start = now - timedelta(hours=num)
            return start, now

        raise ValueError("Invalid range")

    async def query_data(
            self, range_str=str, symbol: Optional[str] = None
    ) -> Optional[DataFrame]:

        if not symbol:
            raise ValueError("Symbol must be provided")

        formatted_range = self.get_dates_from_now(range_str)

        query = self._get_query(formatted_range, symbol)
        api = self._client.query_api()
        try:
            df: DataFrame = await api.query_data_frame(query)

        except Exception as e:
            logger.error(f"Failed to query data. Reason: {e}")
            return None
        finally:
            await self._client.close()
        return df

    def _get_query(self, range=tuple[datetime, datetime], symbol: Optional[str] = None) -> str:
        return f"""from(bucket: "{self._bucket}")
                            |> range(start: {self.format_date(range[0])}, stop: {self.format_date(range[1])})
                            |> filter(fn: (r) => r._measurement == "CandleData" and r.Symbol == "{symbol}")
                            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                            """


async def get_influx_client():
    return await InfluxClient.get_uploader(url=os.getenv('INFUX_URL'), token=os.getenv('INFUX_TOKEN'),
                              org=os.getenv('INFUX_ORG'), bucket=os.getenv('INFUX_BUCKET'))
