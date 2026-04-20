from glob import glob
from .common import SQL_PATH


def get_queries(pattern: str, reverse: bool = False) -> list[str]:
    path = SQL_PATH / pattern
    fs = sorted(glob(str(path)), reverse=reverse)
    queries = list()
    for f in fs:
        queries.append(open(f).read())
    return queries
