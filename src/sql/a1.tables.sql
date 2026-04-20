#------------#
#-- Task 1 --#
#------------#
CREATE TABLE
  IF NOT EXISTS Movie (
    id VARCHAR(16),
    title VARCHAR(512),
    year INTEGER,
    isadult BOOLEAN,
    runtime INTEGER,
    rating FLOAT,
    totalvotes INTEGER,
    year_s FLOAT,
    runtime_s FLOAT,
    rating_s FLOAT,
    totalvotes_s FLOAT,
    PRIMARY KEY (id)
  );


CREATE TABLE
  IF NOT EXISTS Genre (id VARCHAR(16), name VARCHAR(128), PRIMARY KEY (id));


CREATE TABLE
  IF NOT EXISTS IsClassifiedAs (
    mid VARCHAR(16),
    gid VARCHAR(16),
    PRIMARY KEY (mid, gid)
  );


CREATE TABLE
  IF NOT EXISTS IsKnownFor (
    pid VARCHAR(16),
    mid VARCHAR(16),
    PRIMARY KEY (pid, mid)
  );


#------------#
#-- Task 2 --#
#------------#
CREATE TABLE
  IF NOT EXISTS Person (
    id VARCHAR(16),
    name VARCHAR(128),
    birthyear INTEGER,
    deathyear INTEGER,
    PRIMARY KEY (id)
  );