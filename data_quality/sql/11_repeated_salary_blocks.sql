WITH numbered AS (
    SELECT
        row_id,
        salary_estimate,
        company_name_clean,
        row_id - ROW_NUMBER() OVER (PARTITION BY salary_estimate ORDER BY row_id) AS block_id
    FROM postings_normalized
    WHERE salary_estimate <> '-1'
),
blocks AS (
    SELECT
        salary_estimate,
        MIN(row_id) AS first_row_id,
        MAX(row_id) AS last_row_id,
        COUNT(*) AS consecutive_rows,
        COUNT(DISTINCT company_name_clean) AS distinct_companies
    FROM numbered
    GROUP BY salary_estimate, block_id
)
SELECT salary_estimate, first_row_id, last_row_id, consecutive_rows, distinct_companies
FROM blocks
WHERE consecutive_rows >= 10
  AND distinct_companies >= 8
ORDER BY first_row_id;
