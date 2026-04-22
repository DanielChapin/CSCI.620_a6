from .db_utils import connect
from .dataset import title_basics, title_ratings, name_basics
from mysql.connector.abstracts import MySQLCursorAbstract
from typing import Callable
from pandas import DataFrame
from .migrations import get_queries
from .args import MainArgs, entrypoint
from functools import cache
from .env import IMPORT_CHUNK_SIZE, K_MEANS_BATCH_ITERATIONS, K_MEANS_BATCH_SIZE
from tqdm import tqdm
from sklearn.cluster import MiniBatchKMeans
from .common import OUT_PATH
import seaborn as sns
import matplotlib.pyplot as plt
from time import time


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
    print("Refining title ratings")
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
        assert n >= 1
        return "%s, " * (n - 1) + "%s"

    def insert_query(table: str, attributes: list[str]) -> str:
        return f"INSERT INTO {table} ({', '.join(attributes)}) VALUES ({insert_n(len(attributes))})"

    def dropna_query(table: str, attributes: list[str]) -> str:
        clauses = [f"{attrib} IS NULL" for attrib in attributes]
        return f"DELETE FROM {table} WHERE {' OR '.join(clauses)}"

    # id, name, birthyear, deathyear, birthyear_s, deathyear_s
    query = insert_query("Person", ["id", "name", "birthyear", "deathyear"])
    print(query)
    for chunk in tqdm(chunk_df(name_basics_refined()[["nconst", "primaryName", "birthYear", "deathYear"]])):
        cursor.executemany(query, chunk.values.tolist())

    query = insert_query("IsKnownFor", ["pid", "mid"])
    print(query)
    for chunk in tqdm(chunk_df(name_basics_refined()[["nconst", "knownForTitles"]])):
        values = list()
        for [pid, known_fors] in chunk.values:
            values += [[pid, known_for_id]
                       for known_for_id in known_fors.split(",")]
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

    query = "UPDATE Movie SET rating = %s, totalvotes = %s WHERE id = %s"
    print(query)
    chunks = chunk_df(title_ratings_refined()[
                      ['averageRating', 'numVotes', 'tconst']])
    for chunk in tqdm(chunks):
        cursor.executemany(query, chunk.values.tolist())

    query = dropna_query("Movie", ["rating, totalvotes"])
    print(query)
    cursor.execute(query)


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
    path = OUT_PATH / f"{int(time())}_{name}"
    path.mkdir(parents=True)

    def output_img(clusters, samples: DataFrame, phase):
        x_col, y_col = samples.columns[:2]

        fig, ax = plt.subplots(figsize=(8, 8))

        sns.scatterplot(
            data=samples,
            x=x_col,
            y=y_col,
            color="black",
            s=15,
            ax=ax,
        )

        centers_df = DataFrame(clusters, columns=[x_col, y_col])
        centers_df["cluster"] = range(len(clusters))
        sns.scatterplot(
            data=centers_df,
            x=x_col,
            y=y_col,
            hue="cluster",
            palette="tab10",
            s=180,
            edgecolor="white",
            linewidth=1.2,
            zorder=10,
            ax=ax
        )

        fig.tight_layout()
        fig.savefig(path / f"{phase}.jpg", dpi=300)
        plt.close(fig)

    inertias = list()
    for iteration in range(K_MEANS_BATCH_ITERATIONS):
        sample = get_sample()
        kmeans.partial_fit(sample)
        inertias.append(kmeans.inertia_)
        output_img(kmeans.cluster_centers_, sample, iteration)

    # Graph ineratia values
    iterations = range(1, len(inertias) + 1)

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.plot(iterations, inertias, marker="o", linewidth=2)

    ax.set_xlabel("Iteration")
    ax.set_ylabel("Inertia")

    fig.tight_layout()
    fig.savefig(path / "inertia.jpg", dpi=300)
    plt.close(fig)


def data_clustering(cursor: MySQLCursorAbstract):
    print("Movie runtime + rating clusters")
    kmeans = MiniBatchKMeans(n_clusters=4, init=DataFrame(
        [[0.25, 0.25], [0.75, 0.25], [0.25, 0.75], [0.75, 0.75]]))

    def get_data() -> DataFrame:
        query = f"SELECT runtime_s, rating_s FROM Movie ORDER BY RAND() LIMIT {K_MEANS_BATCH_SIZE}"
        cursor.execute(query)
        return DataFrame(cursor.fetchall())

    kmeans_experiment("movie_runtime_rating", kmeans, get_data)


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
