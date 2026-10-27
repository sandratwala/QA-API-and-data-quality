SELECT
    COUNT(*) AS total_rows,
    SUM(rating_value IS NULL) AS rows_with_rating_minus_one,
    ROUND(AVG(CAST(rating AS REAL)), 2) AS naive_average_rating,
    ROUND(AVG(rating_value), 2) AS correct_average_rating,
    ROUND(AVG(rating_value) - AVG(CAST(rating AS REAL)), 2) AS error_in_naive_average
FROM postings_normalized;
