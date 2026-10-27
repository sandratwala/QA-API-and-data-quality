WITH per_company AS (
    SELECT
        company_name_clean,
        COUNT(*) AS postings,
        COUNT(DISTINCT location) AS distinct_locations,
        ROUND(AVG(rating_value), 2) AS average_rating
    FROM postings_normalized
    WHERE trim(company_name_clean) <> ''
    GROUP BY company_name_clean
),
ranked AS (
    SELECT
        *,
        ROUND(100.0 * postings / SUM(postings) OVER (), 2) AS pct_of_all_postings,
        RANK() OVER (ORDER BY postings DESC) AS company_rank
    FROM per_company
)
SELECT company_rank, company_name_clean, postings, pct_of_all_postings, distinct_locations, average_rating
FROM ranked
WHERE pct_of_all_postings >= 0.5
ORDER BY company_rank;
