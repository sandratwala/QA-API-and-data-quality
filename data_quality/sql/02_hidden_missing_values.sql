WITH totals AS (
    SELECT COUNT(*) AS total_rows FROM job_postings
),
sentinels AS (
    SELECT 'rating' AS column_name, SUM(rating IN ('-1', '-1.0')) AS minus_one, SUM(trim(rating) = '') AS blank, 0 AS unknown_text FROM job_postings
    UNION ALL SELECT 'company_name', SUM(company_name = '-1'), SUM(trim(company_name) = ''), 0 FROM job_postings
    UNION ALL SELECT 'salary_estimate', SUM(salary_estimate = '-1'), SUM(trim(salary_estimate) = ''), 0 FROM job_postings
    UNION ALL SELECT 'headquarters', SUM(headquarters = '-1'), SUM(trim(headquarters) = ''), 0 FROM job_postings
    UNION ALL SELECT 'size', SUM(size = '-1'), SUM(trim(size) = ''), SUM(size = 'Unknown') FROM job_postings
    UNION ALL SELECT 'founded', SUM(founded = '-1'), SUM(trim(founded) = ''), 0 FROM job_postings
    UNION ALL SELECT 'type_of_ownership', SUM(type_of_ownership = '-1'), SUM(trim(type_of_ownership) = ''), SUM(type_of_ownership = 'Unknown') FROM job_postings
    UNION ALL SELECT 'industry', SUM(industry = '-1'), SUM(trim(industry) = ''), 0 FROM job_postings
    UNION ALL SELECT 'sector', SUM(sector = '-1'), SUM(trim(sector) = ''), 0 FROM job_postings
    UNION ALL SELECT 'revenue', SUM(revenue = '-1'), SUM(trim(revenue) = ''), SUM(revenue LIKE 'Unknown%') FROM job_postings
    UNION ALL SELECT 'competitors', SUM(competitors = '-1'), SUM(trim(competitors) = ''), 0 FROM job_postings
    UNION ALL SELECT 'easy_apply', SUM(easy_apply = '-1'), SUM(trim(easy_apply) = ''), 0 FROM job_postings
)

SELECT
    column_name,
    minus_one,
    blank,
    unknown_text,
    minus_one + blank + unknown_text AS total_missing,
    ROUND(100.0 * (minus_one + blank + unknown_text) / total_rows, 1) AS pct_missing
FROM sentinels CROSS JOIN totals
WHERE minus_one + blank + unknown_text > 0
ORDER BY total_missing DESC;
