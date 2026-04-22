#align(center + horizon)[
  #text(size: 24pt)[*CSCI.620 A6 Report*]

  #text(size: 20pt)[Daniel Chapin]

  #datetime.today().display()
]

#set heading(numbering: "1.")

#outline()
#pagebreak()

= Overview

Reference `README.md` for instructions on setup and running.

= Feature Selection

These are the features selected for clustering/analysis. \
*Movie.rating + Movie.runtime* - try to cluster movies into categories of long + high rated (best), short + high rated (better), short + low rated (okay), and long + low rated (worst).

= Data Analysis

== Name Basics (Person Table)
```
           birthYear      deathYear
count  663539.000000  253634.000000
mean     1954.371954    1994.786622
std        35.613672      36.565090
min         4.000000      17.000000
25%      1933.000000    1981.000000
50%      1961.000000    2003.000000
75%      1980.000000    2016.000000
max      2025.000000    2026.000000
```
Just from the high level description of the dataset we can see that there are some obvious outliers in this dataset.
Perhaps I don't know enough about movies but I doubt that anyone in the IMDB dataset was actually born in 4AD.

Also, it's clear that there are a lot of death years missing, but perhaps most of the people are still alive.

== Title Basics (Movie Table)
```
            isAdult     startYear        endYear  runtimeMinutes
count  1.221900e+07  1.077031e+07  151625.000000    4.354905e+06
mean   3.264775e-02  2.006603e+03    2008.180722    4.477602e+01
std    1.777129e-01  2.019176e+01      16.429974    1.772008e+03
min    0.000000e+00  1.874000e+03    1928.000000    0.000000e+00
25%    0.000000e+00  2.002000e+03    2001.000000    2.100000e+01
50%    0.000000e+00  2.014000e+03    2014.000000    3.000000e+01
75%    0.000000e+00  2.020000e+03    2020.000000    6.000000e+01
max    1.000000e+00  2.115000e+03    2032.000000    3.692080e+06
```
From this description, we can see that a significant majority of movies are not labeled adult, as up to the 75th percentile there are all 0s.

The start years and the end years mostly make sense but I'm not sure if there should be any end years past the current year, which there clearly are.

There are also some substantial runtime disparities, as a movie that has no length and a movie that is just shy of 4 million minutes (#{ 3.69e6 / 60 } hours) are both probably not real datapoints.

== Title Ratings (Movie Table)
```
       averageRating      numVotes
count   1.624708e+06  1.624708e+06
mean    6.966816e+00  1.039895e+03
std     1.410194e+00  1.814055e+04
min     1.000000e+00  5.000000e+00
25%     6.200000e+00  1.200000e+01
50%     7.200000e+00  2.700000e+01
75%     7.900000e+00  1.030000e+02
max     1.000000e+01  3.144126e+06
```
The description makes the ratings seem pretty reasonable.

= Clustering Results

Here are the following minibatch cluster centers (and batch datapoints).

#set image(width: 33%)

#align(center)[
  #image("out/1776829450_movie_runtime_rating/0.jpg")
  #image("out/1776829450_movie_runtime_rating/1.jpg")
  #image("out/1776829450_movie_runtime_rating/2.jpg")
  #image("out/1776829450_movie_runtime_rating/3.jpg")
  #image("out/1776829450_movie_runtime_rating/4.jpg")
  #image("out/1776829450_movie_runtime_rating/5.jpg")
  #image("out/1776829450_movie_runtime_rating/6.jpg")
  #image("out/1776829450_movie_runtime_rating/7.jpg")
  #image("out/1776829450_movie_runtime_rating/8.jpg")
  #image("out/1776829450_movie_runtime_rating/9.jpg")
]

And finally the graph of inertia:
#align(center)[
  #image("out/1776829450_movie_runtime_rating/inertia.jpg")
]

Evidently, the data is substantially skewed to one side and is not effectively clusterable.
Regardless, the inertia does in fact go down with several iterations of minibatch.
