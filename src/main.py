from .db_utils import connect
from .dataset import title_basics, title_ratings, name_basics
from mysql.connector.abstracts import MySQLCursorAbstract
from typing import Callable
from pandas import DataFrame
from .migrations import get_queries
from .args import MainArgs, entrypoint
from functools import cache
from .env import IMPORT_CHUNK_SIZE
from tqdm import tqdm
from sklearn.cluster import MiniBatchKMeans
from .common import OUT_PATH
import seaborn as sns


drop_tables = get_queries("*.drop_tables.sql", reverse=True)
make_tables = get_queries("*.tables.sql")


def chunk_df(df: DataFrame, chunksize=IMPORT_CHUNK_SIZE) -> list[DataFrame]:
    return [df[i:i+chunksize] for i in range(0, df.shape[0], chunksize)]


@cache
def title_basics_refined():
    print("Refining title basics")
    return title_basics().dropna()


@cache
def title_ratings_refined():
    print("Refining title basics")
    return title_ratings().dropna()


@cache
def name_basics_refined():
    print("Refining name basics")
    return name_basics().dropna()


def data_analysis():
    print("= Before Refinement =")
    print("Name basics")
    print(name_basics().describe())
    print("Title basics")
    print(title_basics().describe())
    print("Title ratings")
    print(title_ratings().describe())

    print("= After Refinement =")
    print("Name basics")
    print(name_basics_refined().describe())
    print("Title basics")
    print(title_basics_refined().describe())
    print("Title ratings")
    print(title_ratings_refined().describe())


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
    # Raw insertion
    print("Inserting raw data...")

    def insert_n(n: int) -> str:
        return "%s, " * (n - 1) + "%s"

    def insert_query(table: str, attributes: list[str]) -> str:
        return f"INSERT INTO {table} ({', '.join(attributes)}) VALUES ({insert_n(len(attributes))})"

    # id, name, birthyear, deathyear, birthyear_s, deathyear_s
    query = insert_query("Person", ["id", "name", "birthyear", "deathyear"])
    print(query)
    for chunk in tqdm(chunk_df(name_basics_refined()[["nconst", "primaryName", "birthYear", "deathYear"]])):
        cursor.executemany(query, chunk.values.tolist())

    query = insert_query("IsKnownFor", ["pid", "mid"])
    print(query)
    for chunk in tqdm(chunk_df(name_basics()[["nconst", "knownForTitles"]])):
        values = list()
        for [pid, known_fors] in chunk.values:
            values += [[pid, known_for_id]
                       for known_for_id in known_fors.spit(",")]
        cursor.executemany(query, values)

    query = insert_query(
        "Movie", ["id", "title", "year", "isadult", "runtime"])
    print(query)
    for chunk in tqdm(chunk_df(
        title_basics_refined()[["tconst", "primaryTitle",
                                "startYear", "isAdult", "runtimeMinutes"]]
    )):
        cursor.executemany(query, chunk.values.tolist())

    query = insert_query("Genre", ["id", "name"])
    print(query)
    genre_num = 1
    genre_lookup = {}
    for genres in title_basics_refined()["genres"]:
        for genre in genres.split(","):
            if genre not in genre_lookup:
                genre_lookup[genre] = str(f"g{genre_num:06}")
                genre_num += 1
    cursor.executemany(
        query, [[gid, name]
                for (name, gid) in genre_lookup.items()])

    query = insert_query("IsClassifiedAs", ["mid", "gid"])
    print(query)
    chunks = chunk_df(title_basics_refined()[["tconst", "genres"]])
    for chunk in tqdm(chunks):
        values = list()
        for [mid, genres] in chunk.values:
            values += [[mid, genre_lookup[gname]]
                       for gname in genres.split(",")]
        cursor.executemany(query, values)


def load_scaled(cursor: MySQLCursorAbstract):
    def minmax_scale_query(table: str, src_attribute: str, dst_attribute: str) -> str:
        return f"UPDATE {table} target, (SELECT MIN({src_attribute}) as min_val, MAX({src_attribute}) as max_val FROM {table}) stats\n\tSET target.{dst_attribute} = (target.{src_attribute} - stats.min_val) / (stats.max_val - stats.min_val)"

    def scale(*args):
        query = minmax_scale_query(*args)
        print(query)
        cursor.execute(query)

    scale("Person", "birthyear", "birthyear_s")
    scale("Person", "deathyear", "deathyear_s")
    scale("Movie", "year", "year_s")
    scale("Movie", "runtime", "runtime_s")
    scale("Movie", "rating", "rating_s")
    scale("Movie", "totalvotes", "totalvotes_s")


def kmeans_experiment(name: str, kmeans: MiniBatchKMeans, get_sample: Callable[[], DataFrame]):
    path = OUT_PATH / name
    path.mkdir(parents=True)

    inertias = list()


def data_clustering(conn: MySQLCursorAbstract):
    print("Movie runtime + rating clusters")
    name = "movie_runtime_rating"
    kmeans = MiniBatchKMeans(n_clusters=4, init=DataFrame(
        [[0.25, 0.25], [0.75, 0.25], [0.25, 0.75], [0.75, 0.75]]))


def main(args: MainArgs):
    def with_conn(fn):
        with connect() as conn, conn.cursor() as cursor:
            conn.start_transaction()
            res = fn(cursor)
            conn.commit()
            return res

    if args.analyze:
        print("== Data Analysis ==")
        data_analysis()
    if args.init:
        print("== Init Tables ==")
        with_conn(init_tables)
    if args.load:
        print("== Load Data into DB ==")
        with_conn(load_data)
    if args.scale:
        print("== Scaling MySQL Data ==")
        with_conn(load_scaled)
    if args.cluster:
        print("== Data Clustering ==")
        with_conn(data_clustering)


if __name__ == "__main__":
    entrypoint(main)
