from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os
import influxdb_client
import pandas as pd

load_dotenv()

database_url = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

client = influxdb_client.InfluxDBClient(url=os.getenv('INFUX_URL'), token=os.getenv('INFUX_TOKEN'), org=os.getenv('INFUX_ORG'), timeout=1000000)
