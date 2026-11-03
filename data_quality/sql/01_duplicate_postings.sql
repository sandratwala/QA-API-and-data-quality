WITH ranked AS (
    SELECT
        row_id,
        job_title,
        company_name_clean,
        location,
        salary_estimate,
        rating,
        company_name,
        ROW_NUMBER() OVER duplicate_group AS copy_number,
        FIRST_VALUE(row_id) OVER duplicate_group AS first_row_id,
        FIRST_VALUE(salary_estimate) OVER duplicate_group AS first_salary_estimate,
        FIRST_VALUE(rating) OVER duplicate_group AS first_rating
    FROM postings_normalized
    WINDOW duplicate_group AS (
        PARTITION BY job_title_key, company_name_clean, location, description_key
        ORDER BY row_id
    )
)

SELECT
    row_id,
    first_row_id AS duplicate_of_row_id,
    job_title,
    company_name_clean,
    location,
    first_salary_estimate,
    salary_estimate,
    first_rating,
    rating,
    CASE WHEN salary_estimate <> first_salary_estimate THEN 1 ELSE 0 END AS salary_conflict,
    CASE WHEN rating <> first_rating THEN 1 ELSE 0 END AS rating_conflict
FROM ranked
WHERE copy_number > 1
ORDER BY first_row_id, row_id;
