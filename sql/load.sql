\copy proj1.artist FROM '/home/cs143/data/artist.csv' DELIMITER ',' QUOTE '"' CSV;
\copy proj1.song   FROM '/home/cs143/data/song.csv'   DELIMITER ',' QUOTE '"' CSV;
\copy proj1.token  FROM '/home/cs143/data/token.csv'  DELIMITER ',' QUOTE '"' CSV;

/* Compute TFIDF table */
SELECT T.song_id AS song_id, 
       T.token AS token, 
       T.count AS count,
       Q.DF    AS DF,
      (T.count*log(57650/DF::float)) AS score
INTO TABLE proj1.tfidf
FROM proj1.token AS T
LEFT JOIN (
    SELECT token,count(song_id) AS DF
    FROM proj1.token
    GROUP BY token
) AS Q
ON T.token=Q.token
;