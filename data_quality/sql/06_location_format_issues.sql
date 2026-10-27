SELECT
    location,
    COUNT(*) AS postings,
    CASE
        WHEN location IN ('Remote', 'United States') THEN 'not a city'
        WHEN length(location) - length(replace(location, ',', '')) = 0 THEN 'state or region only, no city'
        WHEN length(location) - length(replace(location, ',', '')) > 1 THEN 'extra part (county) in location'
        ELSE 'unexpected format'
    END AS issue
FROM postings_normalized
WHERE NOT (
    location GLOB '*, [A-Z][A-Z]'
    AND length(location) - length(replace(location, ',', '')) = 1
)
GROUP BY location
ORDER BY postings DESC, location;
