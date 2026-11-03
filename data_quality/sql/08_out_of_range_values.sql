SELECT row_id, 'rating' AS field, rating AS value, 'rating must be between 1 and 5, or -1 when missing' AS rule
FROM postings_normalized
WHERE rating_value IS NOT NULL AND (rating_value < 1 OR rating_value > 5)
UNION ALL

SELECT row_id, 'founded', founded, 'company cannot be founded after the data was scraped (2020)'
FROM postings_normalized
WHERE founded_year > 2020
UNION ALL

SELECT row_id, 'easy_apply', easy_apply, 'easy_apply must be True or -1'
FROM postings_normalized
WHERE easy_apply NOT IN ('True', '-1')
UNION ALL

SELECT row_id, 'salary_estimate', salary_estimate, 'annual salary must be between $10K and $500K'
FROM postings_normalized
WHERE pay_period = 'annual' AND (salary_low < 10 OR salary_high > 500)
ORDER BY field, row_id;
