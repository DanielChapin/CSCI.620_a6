"""
Loading this module has side effects!
"""
from .common import DOT_ENV_PATH
from dotenv import load_dotenv
from os import getenv

load_dotenv(DOT_ENV_PATH)


def require_value(value):
    assert value is not None
    return value


def reqenv(key: str) -> str:
    return require_value(getenv(key))


def optenv(key: str, default):
    val = getenv(key)
    if val is None:
        return default
    return val


DB_NAME = reqenv("DB_NAME")
DB_UNAME = reqenv("DB_UNAME")
DB_PWORD = reqenv("DB_PWORD")

DB_HOST = optenv("DB_HOST", "127.0.0.1")

IMPORT_CHUNK_SIZE = int(optenv("IMPORT_CHUNK_SIZE", "10000"))
