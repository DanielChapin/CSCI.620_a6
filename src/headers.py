from .dataset import title_basics, title_ratings, name_basics, title_crew, title_principals


def main():
    def cols(fn) -> list[str]:
        return fn(nrows=0).columns
    print(cols(title_basics))
    # A demonstration on why we need to separate on tabs and also literal '\t'
    # print(title_basics(skiprows=109 * 10000 + 6405, nrows=10))
    print(cols(title_ratings))
    print(cols(name_basics))
    print(cols(title_crew))
    print(cols(title_principals))


if __name__ == "__main__":
    main()
