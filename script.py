import psycopg2
import matplotlib.pyplot as plt

# Connect to PostgreSQL
conn = psycopg2.connect(
    database="shefalisharma",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)

# Create a cursor object
cur = conn.cursor()

# Execute SQL query
cur.execute("SELECT * FROM apple_music_dataset LIMIT 4")

# Fetch data
data = cur.fetchall()


# Execute Q1: Analysing Genre's and their track released over the years
cur.execute("""
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
""")

# Fetch Q1 data
q1_data = cur.fetchall()

# Plot Q1 results
# (Replace with appropriate plotting code)

# Execute Q2: Distribution of track prices within each genre (explicit tracks only)
cur.execute("""
SELECT "primaryGenreName", SUM("trackPrice") AS sum_track_price, COUNT("trackId") AS count_tracks_released, 
ROUND(SUM("trackPrice")/COUNT("trackId")::decimal, 2) AS price_per_track, 
RANK() OVER(ORDER BY SUM("trackPrice")/COUNT("trackId") DESC) AS rank_avg_price
FROM apple_music_dataset
WHERE "trackExplicitness" = 'explicit'
GROUP BY "primaryGenreName"
ORDER BY sum_track_price DESC
""")

# Fetch Q2 data
q2_data = cur.fetchall()

# Plot Q2 results
# (Replace with appropriate plotting code)

# Close cursor and connection
cur.close()
conn.close()



