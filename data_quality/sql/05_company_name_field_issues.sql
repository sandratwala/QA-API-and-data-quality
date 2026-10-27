SELECT
    row_id,
    replace(company_name, char(10), '\n') AS company_name_raw,
    company_name_clean,
    rating,
    CASE
        WHEN trim(company_name) = '' THEN 'company name missing'
        ELSE 'rating appended to company name'
    END AS issue
FROM postings_normalized
WHERE trim(company_name) = ''
   OR instr(company_name, char(10)) > 0
ORDER BY issue DESC, row_id;
