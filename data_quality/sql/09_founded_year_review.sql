SELECT
    company_name_clean,
    founded_year,
    headquarters,
    COUNT(*) AS postings
FROM postings_normalized
WHERE founded_year < 1800
GROUP BY company_name_clean, founded_year, headquarters
ORDER BY founded_year, company_name_clean;
