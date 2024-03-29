[Back to my profile](https://shefaliisharma.github.io/shefaliisharma/)

# Apple Music Dataset Analysis

 [![Available on GitHub](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/shefaliisharma/holymoly)

<!-- TOC -->
* [Apple Music Dataset Analysis](#apple-music-dataset-analysis)
  * [Research Objectives](#research-objectives)
  * [Methodology](#methodology)
  * [Results](#results)
    * [Temporal trends in music genres](#temporal-trends-in-music-genres)
        * [Observation:](#observation)
    * [Distribution of Track Prices & Average Price within each Genre (Explicit Only)](#distribution-of-track-prices--average-price-within-each-genre-explicit-only)
        * [Observation:](#observation-1)
    * [Popularity of Genre, measured by the number of tracks released, vary across different release years](#popularity-of-genre-measured-by-the-number-of-tracks-released-vary-across-different-release-years)
        * [Observation:](#observation-2)
    * [Correlation between the track price and the track duration within each genre](#correlation-between-the-track-price-and-the-track-duration-within-each-genre)
        * [Observation:](#observation-3)
    * [Temporal patterns in the release duration of tracks within Collections](#temporal-patterns-in-the-release-duration-of-tracks-within-collections)
        * [Observation:](#observation-4)
  * [Conclusion](#conclusion)
<!-- TOC -->


This repository contains the analysis of a [Kaggle dataset on Apple Music](https://www.kaggle.com/datasets/kanchana1990/apple-music-dataset-10000-tracks-uncovered). The dataset provides information about tracks, collections, artists, genres, and other attributes related to Apple Music.

While the dataset is available as a csv, in a real-life scenario, the data would be stored in a database, for example, PostgreSQL database. Therefore, I have performed the analysis using SQL queries to extract relevant information and answer the related research questions. Thus the solutions provided here will scale well to larger datasets and can be easily integrated into a production environment.

The SQL table preview corressponding to the dataset is as follows:

| artistId | artistName | collectionCensoredName | collectionId | collectionName | collectionPrice | contentAdvisoryRating | country | currency | discCount | discNumber | isStreamable | kind | previewUrl | primaryGenreName | releaseDate | trackCensoredName | trackCount | trackExplicitness | trackId | trackName | trackNumber | trackPrice | trackTimeMillis |
|----------|------------|------------------------|--------------|----------------|-----------------|-----------------------|---------|----------|-----------|------------|--------------|------|------------|------------------|-------------|-------------------|------------|------------------|---------|-----------|-------------|------------|----------------|
| 219350813 | The Neighbourhood | I Love You. | 635016635 | I Love You. | 9.99 |  | USA | USD | 1 | 1 | TRUE | song | [Preview](https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview112/v4/b9/1a/41/b91a4115-f91b-4bd1-dc03-38964c1328a5/mzaf_12342250626902314230.plus.aac.p.m4a) | Alternative | 2013-04-22 12:30:00+05:30 | Float | 11 | notExplicit | 635016647 | Float | 11 | 1.29 | 261200 |
| 4218340 | Israel Kamakawiwo'ole | Wonderful World | 258387384 | Wonderful World | 11.99 |  | USA | USD | 1 | 1 | TRUE | song | [Preview](https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview125/v4/cd/47/c3/cd47c324-7645-b010-4d5b-5e7db1eb6c89/mzaf_16520999357341225048.plus.aac.p.m4a) | Worldwide | 2001-09-25 17:30:00+05:30 | Wonderful World | 12 | notExplicit | 258387389 | Wonderful World | 1 | 0.99 | 270667 |
| 396754057 | One Direction | Midnight Memories (Deluxe Edition) | 695318295 | Midnight Memories (Deluxe Edition) | 14.99 |  | USA | USD | 2 | 1 | TRUE | song | [Preview](https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview115/v4/f8/a5/e5/f8a5e57a-b74f-b93e-3252-85a195a7dbc2/mzaf_1283055366578986529.plus.aac.p.m4a) | Pop | 2013-11-25 13:30:00+05:30 | Midnight Memories | 18 | notExplicit | 695318304 | Midnight Memories | 4 | 1.29 | 176320 |
| 28721078 | Sia | 1000 Forms of Fear | 882945378 | 1000 Forms of Fear | 9.99 |  | USA | USD | 1 | 1 | TRUE | song | [Preview](https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview126/v4/76/5b/17/765b173e-f861-a846-1627-03fce14795a4/mzaf_6635366094375706754.plus.aac.p.m4a) | Pop | 2014-07-04 12:30:00+05:30 | Cellophane | 12 | notExplicit | 882945396 | Cellophane | 11 | 1.29 | 265587 |
| 80456331 | Panic! At the Disco | Pretty. Odd. (Deluxe Version) | 275965231 | Pretty. Odd. (Deluxe Version) | 12.99 |  | USA | USD | 1 | 1 | TRUE | song | [Preview](https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview115/v4/dc/79/62/dc7962c0-452b-9062-d656-0f93b70e4d65/mzaf_13536033148520859834.plus.aac.p.m4a) | Alternative | 2008-03-25 12:30:00+05:30 | Northern Downpour | 18 | notExplicit | 275965263 | Northern Downpour | 7 | 1.29 | 247773 |

DDL for the above table is as follows: 

```sql
CREATE TABLE apple_music_dataset (
    "artistId" integer,
    "artistName" text,
    "collectionCensoredName" text,
    "collectionId" integer,
    "collectionName" text,
    "collectionPrice" numeric,
    "contentAdvisoryRating" character varying,
    country text,
    currency text,
    "discCount" integer,
    "discNumber" integer,
    "isStreamable" character varying,
    kind text,
    "previewUrl" text,
    "primaryGenreName" character varying,
    "releaseDate" timestamp with time zone,
    "trackCensoredName" text,
    "trackCount" integer,
    "trackExplicitness" character varying,
    "trackId" integer,
    "trackName" text,
    "trackNumber" integer,
    "trackPrice" numeric,
    "trackTimeMillis" integer
);
```

## Research Objectives

1. Examine the trends in music genres over the years, specifically focusing on the number of tracks released within each genre. This analysis aims to identify genres that have seen a decline or increase in their popularity within the music industry over time.
2. Understand the distribution of track prices within each music genre, specifically focusing on tracks with explicit content.
3. Investigate how the popularity of tracks, as indicated by the number of purchases, fluctuates across different release years within each genre. This will provide a historical perspective on the popularity trends of different music genres, potentially revealing shifts in consumer preferences over time.
4. Examine how the average track duration has evolved over the years for the top 5 artists with the highest number of tracks. This will provide insights into the changing trends in track lengths among the most prolific artists, potentially reflecting broader shifts in the music industry's production norms.
5. Investigate the correlation between track price and track duration within each genre, aiming to uncover any discernible patterns or associations. This analysis will provide insights into how pricing relates to duration across different musical genres, potentially revealing genre-specific trends.
6. Analyze the release patterns of tracks for artists with similar popularity levels but different genres. This will help identify genre-specific release strategies and patterns that artists adopt to maximize their reach and impact in the music industry.
7. Analyze the relationship between the price of individual tracks and their counterparts within collections, aiming to discern any disparities or trends in pricing.
8. Investigate the correlation between the number of tracks in a collection and the average track price within each genre. This analysis aims to uncover potential patterns or trends in pricing strategies across different genres, shedding light on how the size of a music collection influences the average price per track.
9. Explore the relationship between the popularity of tracks and the explicitness of the tracks within each genre. This analysis aims to identify any patterns or trends in consumer preferences based on the explicit content of tracks, potentially revealing genre-specific patterns in popularity.
10. Identify any outliers in terms of track duration among tracks released by the top 5 artists. This analysis aims to uncover any unusual or exceptional tracks in terms of duration that stand out from the rest of the artists' discography.

## Methodology

The analysis was performed using SQL queries on the Apple Music dataset. The dataset was queried to extract relevant information and answer the research questions. The queries used in the analysis are provided in the results section below.

The data from SQL cursors was loaded into a Pandas DataFrame for further visualization and the charts were created using libraries such as Matplotlib and Seaborn.

My local setup for achieving the above consisted of: 

- PostgreSQL server running on localhost on my Mac OS Sonoma
- Postico PostgreSQL client for querying the database and exploratory data analysis
- JetBrains PyCharm IDE for writing and running Python code

## Research

The results of the analysis are summarized below. I have included the SQL queries that were used to generate the results and the final visualizations. Incase you are interested in the python code that was used to create the charts and visualizations, it is available in the github repository.

### Temporal trends in music genres

```sql
WITH genre_table AS (
    SELECT "primaryGenreName", DATE_TRUNC('year', "releaseDate")::date AS release_year, COUNT("trackId") AS track_count
    FROM apple_music_dataset
    GROUP BY "primaryGenreName", DATE_TRUNC('year', "releaseDate")
),
years AS (
    SELECT GENERATE_SERIES(MIN("releaseDate"), MAX("releaseDate"), '1 year'::interval)::date AS years
    FROM apple_music_dataset
),
all_genres AS (
    SELECT DISTINCT "primaryGenreName" AS genre FROM apple_music_dataset
),
cross_join_genre_years AS (
    SELECT years.years, all_genres.genre
    FROM years, all_genres
)
SELECT genre, years, COALESCE(genre_table.track_count, 0) AS count, AVG(COALESCE(genre_table.track_count, 0)) OVER(PARTITION BY genre)
FROM cross_join_genre_years cjgy
LEFT JOIN genre_table ON genre_table."primaryGenreName" = cjgy.genre AND genre_table.release_year = cjgy.years
```

![Fig 1](assets/fig1.png)

##### Observation:
- For all the genres the pattern is the number of tracks have increased significantly around 1990's. This pattern is seen for all genres. 
- Here I have selected only three Genres for display.

### Distribution of Track Prices & Average Price within each Genre (Explicit Only)

```sql
SELECT "primaryGenreName", SUM("trackPrice") AS sum_track_price, 
COUNT("trackId") AS count_tracks_released, 
ROUND(SUM("trackPrice")/COUNT("trackId")::decimal, 2) AS price_per_track, 
RANK() OVER(ORDER BY SUM("trackPrice")/COUNT("trackId") DESC) AS rank_avg_price

FROM apple_music_dataset
WHERE "trackExplicitness" = 'explicit'
GROUP BY "primaryGenreName"
ORDER BY sum_track_price DESC;
```
![Fig 2](assets/fig2.png)

##### Observation:
- Hip-Hop/Rap has the highest track price but it is rank 11th with the average price per track.

### Popularity of Genre, measured by the number of tracks released, vary across different release years

```sql
WITH ranked_genre AS(
SELECT "primaryGenreName", EXTRACT('year' FROM "releaseDate")::integer AS release_year, COUNT("trackId") AS no_tracks_released, RANK() OVER(PARTITION BY EXTRACT('year' FROM "releaseDate") ORDER BY COUNT("trackId") DESC)
FROM apple_music_dataset
GROUP BY "primaryGenreName", EXTRACT('year' FROM "releaseDate")
)

SELECT * FROM ranked_genre WHERE rank = 1 ORDER BY release_year DESC;
```

![Fig 3](assets/fig3.png)

##### Observation:
With the heatmap, it can be seen that Pop has improved in popularity after late 2000s.
Here, for ease of visualization I have chosen only the most popular of the genre of the year.

### Correlation between the track price and the track duration within each genre

```sql
WITH ranked_genre AS(
SELECT "primaryGenreName", EXTRACT('year' FROM "releaseDate")::integer AS release_year, COUNT("trackId") AS no_tracks_released, RANK() OVER(PARTITION BY EXTRACT('year' FROM "releaseDate") ORDER BY COUNT("trackId") DESC)
FROM apple_music_dataset
GROUP BY "primaryGenreName", EXTRACT('year' FROM "releaseDate")
)
SELECT * FROM ranked_genre WHERE rank = 1 ORDER BY release_year DESC;
```
![Fig 4](assets/fig4.png)

##### Observation:
The bar graph displays the correlation is variable across the genre with the highest being within Comedy & Indie Rock (inversely correlated).

### Temporal patterns in the release duration of tracks within Collections

```sql
WITH collection_table AS(
SELECT "collectionId","collectionName", MAX("releaseDate")::date AS last_release, MIN("releaseDate")::date AS first_release, MAX("releaseDate") - MIN("releaseDate") AS collection_release_duration
FROM apple_music_dataset
GROUP BY "collectionName", "collectionId"
ORDER BY collection_release_duration DESC),

collection_table2 AS
( 
SELECT DISTINCT "collectionId", "collectionName", "primaryGenreName"
FROM apple_music_dataset
)
SELECT "primaryGenreName", collection_table."collectionName", first_release, last_release, collection_release_duration
FROM collection_table JOIN collection_table2
ON collection_table."collectionId" = collection_table2."collectionId";
```

![Fig 5](assets/fig5_ii.png)

##### Observation:
Few durations are large in numbers. For instance, Traditional Comedy has ONLY one collection named: "Ultimate Waylon Jennings".
> I was curious, so I searched the collection in Apple Music ([source](https://music.apple.com/in/album/ultimate-waylon-jennings/284985709)) and found that last song: 'America' was released in 1984 & the first song: 'Highwayman'
 in 1964. 




## Conclusion

The analysis of the Apple Music dataset provided insights into various aspects of the music industry, including temporal patterns in release dates, pricing distribution, track duration outliers, and genre-specific release patterns. These findings can be valuable for music industry professionals, researchers, and enthusiasts interested in understanding trends and patterns in the music market.