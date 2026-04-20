from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Project resources
RES_PATH = PROJECT_ROOT / "res"
TITLE_BASICS_PATH = RES_PATH / "title.basics.tsv.gz"
TITLE_RATINGS_PATH = RES_PATH / "title.ratings.tsv.gz"
NAME_BASICS_PATH = RES_PATH / "name.basics.tsv.gz"
TITLE_CREW_PATH = RES_PATH / "title.crew.tsv.gz"
TITLE_PRINCIPALS_PATH = RES_PATH / "title.principals.tsv.gz"

# Environment variables
DOT_ENV_PATH = PROJECT_ROOT / ".env"

# SQL
SQL_PATH = PROJECT_ROOT / "src" / "sql"
