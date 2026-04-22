from .common import TITLE_BASICS_PATH, TITLE_CREW_PATH, TITLE_PRINCIPALS_PATH, TITLE_RATINGS_PATH, NAME_BASICS_PATH
from pandas import DataFrame, read_csv
from pandas.io.parsers.readers import TextFileReader
from .db_utils import map_nulls
from typing import cast


class CSVIter:
    src: TextFileReader
    rows: list[str] | None
    curr_block: list[list] | None
    idx: int

    def __init__(self, src: TextFileReader, rows: list[str] | None = None) -> None:
        self.src = src
        self.rows = rows
        self.curr_block = None
        self.idx = -1

    def __iter__(self):
        def next():
            x = self.next_row()
            if x is None:
                raise StopIteration()
            return x

        return iter(next, None)

    def next_row(self) -> list | None:
        if self.idx < 0 or (self.curr_block is not None and self.idx >= len(self.curr_block)):
            try:
                df = next(self.src)
                if self.rows is not None:
                    df = df[self.rows]
                self.curr_block = map_nulls(df).values.tolist()
                self.idx = 0
            except StopIteration:
                self.curr_block = None

        if self.curr_block is not None:
            row = self.curr_block[self.idx]
            self.idx += 1
            return row

        return None


def read_std(filepath, *args, **kwargs) -> DataFrame:
    # Truly incredible that this function can return a DataFrame
    # without the type signature indicating that
    return cast(DataFrame, read_csv(filepath, sep='\t', compression='gzip', na_values=["\\N"], on_bad_lines='skip', engine='python', keep_default_na=False, *args, **kwargs))
    # return read_csv(filepath, sep='\t', compression='gzip', na_values=[r"\N"], on_bad_lines='skip', keep_default_na=False, *args, **kwargs)


def title_basics(*args, **kwargs) -> DataFrame:
    return read_std(TITLE_BASICS_PATH, *args, **kwargs)


def title_ratings(*args, **kwargs) -> DataFrame:
    return read_std(TITLE_RATINGS_PATH, *args, **kwargs)


def name_basics(*args, **kwargs) -> DataFrame:
    return read_std(NAME_BASICS_PATH, *args, **kwargs)


def title_crew(*args, **kwargs) -> DataFrame:
    return read_std(TITLE_CREW_PATH, *args, **kwargs)


def title_principals(*args, **kwargs) -> DataFrame:
    return read_std(TITLE_PRINCIPALS_PATH, *args, **kwargs)
