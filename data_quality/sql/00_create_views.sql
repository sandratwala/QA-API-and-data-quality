DROP VIEW IF EXISTS postings_normalized;

CREATE VIEW postings_normalized AS
SELECT
    row_id,
    job_title,
    lower(trim(job_title)) AS job_title_key,
    company_name,
    trim(
        CASE
            WHEN instr(company_name, char(10)) > 0
                THEN substr(company_name, 1, instr(company_name, char(10)) - 1)
            ELSE company_name
        END
    ) AS company_name_clean,
    location,
    headquarters,
    size,
    founded,
    CASE WHEN founded = '-1' THEN NULL ELSE CAST(founded AS INTEGER) END AS founded_year,
    rating,
    CASE WHEN rating IN ('-1', '-1.0') THEN NULL ELSE CAST(rating AS REAL) END AS rating_value,
    salary_estimate,
    CASE
        WHEN salary_estimate = '-1' THEN NULL
        WHEN salary_estimate LIKE '%Per Hour%' THEN 'hourly'
        ELSE 'annual'
    END AS pay_period,
    CASE
        WHEN salary_estimate = '-1' THEN NULL
        ELSE CAST(substr(salary_estimate, 2) AS INTEGER)
    END AS salary_low,
    CASE
        WHEN salary_estimate = '-1' THEN NULL
        ELSE CAST(substr(salary_estimate, instr(salary_estimate, '-$') + 2) AS INTEGER)
    END AS salary_high,
    trim(
        replace(replace(replace(replace(replace(replace(replace(replace(replace(
            lower(job_description),
            char(13), ' '), char(10), ' '), char(9), ' '),
            '  ', ' '), '  ', ' '), '  ', ' '), '  ', ' '), '  ', ' '), '  ', ' ')
    ) AS description_key,
    type_of_ownership,
    industry,
    sector,
    revenue,
    competitors,
    easy_apply
FROM job_postings;
