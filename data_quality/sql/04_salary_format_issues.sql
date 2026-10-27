SELECT
    row_id,
    job_title,
    company_name_clean,
    salary_estimate,
    CASE
        WHEN salary_estimate = '-1' THEN 'salary missing (stored as -1)'
        WHEN pay_period = 'hourly' THEN 'hourly rate mixed into annual salary column'
        WHEN salary_low IS NULL OR salary_high IS NULL OR salary_low = 0 OR salary_high = 0 THEN 'could not parse salary'
        WHEN salary_low > salary_high THEN 'minimum salary above maximum'
    END AS issue
FROM postings_normalized
WHERE salary_estimate = '-1'
   OR pay_period = 'hourly'
   OR salary_low IS NULL OR salary_high IS NULL OR salary_low = 0 OR salary_high = 0
   OR salary_low > salary_high
ORDER BY issue, row_id;
