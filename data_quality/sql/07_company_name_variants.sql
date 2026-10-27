WITH companies AS (
    SELECT DISTINCT company_name_clean, headquarters, founded_year, size, revenue
    FROM postings_normalized
    WHERE founded_year IS NOT NULL
      AND headquarters <> '-1'
      AND size NOT IN ('-1', 'Unknown')
      AND trim(company_name_clean) <> ''
),
groups AS (
    SELECT
        headquarters,
        founded_year,
        size,
        revenue,
        COUNT(DISTINCT company_name_clean) AS name_count,
        GROUP_CONCAT(company_name_clean, ' | ') AS name_variants
    FROM companies
    GROUP BY headquarters, founded_year, size, revenue
    HAVING COUNT(DISTINCT company_name_clean) > 1
)
SELECT g.headquarters, g.founded_year, g.size, g.revenue, g.name_count, g.name_variants,
       COUNT(p.row_id) AS postings_affected
FROM groups AS g
JOIN postings_normalized AS p
  ON p.headquarters = g.headquarters
 AND p.founded_year = g.founded_year
 AND p.size = g.size
 AND p.revenue = g.revenue
GROUP BY g.headquarters, g.founded_year, g.size, g.revenue, g.name_count, g.name_variants
ORDER BY postings_affected DESC;
