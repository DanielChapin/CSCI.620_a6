from .env import DB_NAME, DB_PWORD, DB_UNAME, DB_HOST
from mysql.connector import connect as mysql_connect
from pandas import DataFrame


def map_nulls(df: DataFrame) -> DataFrame:
    # This doesn't typecheck despite working
    # Simply ignore :)
    return df.astype(object).where(df.notna(), None)


def connect():
    return mysql_connect(user=DB_UNAME, password=DB_PWORD,
                         host=DB_HOST,
                         database=DB_NAME)
