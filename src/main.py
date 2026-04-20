from .db_utils import connect, map_nulls
from .dataset import CSVIter, title_basics, title_crew, title_principals, title_ratings, name_basics, NAME_BASICS_PATH, TITLE_BASICS_PATH, TITLE_RATINGS_PATH
from .env import IMPORT_CHUNK_SIZE
from mysql.connector.abstracts import MySQLCursorAbstract
from typing import cast
from pandas import DataFrame
from .migrations import get_queries
from .args import MainArgs, entrypoint


drop_tables = get_queries("*.drop_tables.sql", reverse=True)
make_tables = get_queries("*.tables.sql")


def data_analysis():
    print(name_basics().describe())
    print(title_basics().describe())
    print(title_ratings().describe())


def init_tables(cursor: MySQLCursorAbstract):
    # For some reason I can't execute all of the statements as one query
    # or else the cursor becomes unusable...
    # supposedly there use to be a `multi` kwarg but not anymore?
    query_no = 1
    for queries in drop_tables + make_tables:
        for stmt in map(str.strip, queries.split(';')):
            if stmt == '':
                continue
            print(f"Query {query_no}:")
            print(stmt)
            cursor.execute(stmt)
            query_no += 1


def load_data(cursor: MySQLCursorAbstract):
    pass


def data_clustering():
    pass


def main(args: MainArgs):
    if args.analyze:
        print("== Data Analysis ==")
        data_analysis()
    if args.init:
        print("== Init Tables ==")
        with connect() as conn, conn.cursor() as cursor:
            conn.start_transaction()
            init_tables(cursor)
            conn.commit()
    if args.load:
        print("== Load Data into DB ==")
        with connect() as conn, conn.cursor() as cursor:
            conn.start_transaction()
            load_data(cursor)
            conn.commit()
    if args.cluster:
        print("== Data Clustering ==")
        data_clustering()


if __name__ == "__main__":
    entrypoint(main)
