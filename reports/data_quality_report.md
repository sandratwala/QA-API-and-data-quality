# Data quality report

Dataset: Glassdoor Data Analyst job postings, 5,631 rows. Generated 2026-10-17 20:51 UTC.

| # | Check | Severity | Status | Rows returned |
|---|---|---|---|---|
| 01 | Duplicate postings hidden by a changing company field | error | FLAGGED | 123 |
| 02 | Missing values disguised as -1 or Unknown | warning | FLAGGED | 12 |
| 03 | Effect of -1 ratings on the average | info | INFO | 1 |
| 04 | Salary values that are missing or in the wrong unit | error | FLAGGED | 59 |
| 05 | Company name field contaminated or empty | error | FLAGGED | 5,036 |
| 06 | Locations not in 'City, ST' format | warning | FLAGGED | 31 |
| 07 | Same company under different names | warning | FLAGGED | 155 |
| 08 | Values outside valid ranges | error | PASS | 0 |
| 09 | Very old founding years to verify | info | INFO | 28 |
| 10 | Companies with an unusually large share of postings | info | INFO | 8 |
| 11 | Same salary repeated across consecutive rows | error | FLAGGED | 204 |

## 01. Duplicate postings hidden by a changing company field

**Status:** FLAGGED · **Severity:** error · **Rows returned:** 123

Same title, company, location and description appear more than once. Each row listed is an extra copy.

Query: `data_quality/sql/01_duplicate_postings.sql` · Full results: `reports/check_results/01_duplicate_postings.csv`

| row_id | duplicate_of_row_id | job_title | company_name_clean | location | first_salary_estimate | salary_estimate | first_rating | rating | salary_conflict | rating_conflict |
|---|---|---|---|---|---|---|---|---|---|---|
| 5145 | 39 | Data Science Analyst/Engineer | NYU Langone Health | New York, NY | $46K-$87K (Glassdoor est.) | $73K-$127K (Glassdoor est.) | 4.0 | 4.1 | 1 | 1 |
| 5095 | 42 | Behavioral Data Analyst | AB InBev | New York, NY | $46K-$87K (Glassdoor est.) | $47K-$82K (Glassdoor est.) | -1.0 | 4.0 | 1 | 1 |
| 5099 | 54 | Senior Data Analyst | Gemini | New York, NY | $46K-$87K (Glassdoor est.) | $47K-$82K (Glassdoor est.) | 3.6 | 3.7 | 1 | 1 |
| 5080 | 66 | Data Analyst, Retail Media | Criteo | New York, NY | $51K-$88K (Glassdoor est.) | $85K-$146K (Glassdoor est.) | 3.9 | 3.8 | 1 | 1 |
| 5092 | 68 | Portfolio Data Analyst | Neuberger Berman | New York, NY | $51K-$88K (Glassdoor est.) | $46K-$87K (Glassdoor est.) | 3.7 | 3.5 | 1 | 1 |
| 5074 | 78 | Data Analyst | Randstad | Jersey City, NJ | $51K-$88K (Glassdoor est.) | $46K-$65K (Glassdoor est.) | 3.7 | 3.6 | 1 | 1 |
| 5097 | 90 | Data Analyst | FINRA | New York, NY | $51K-$88K (Glassdoor est.) | $47K-$82K (Glassdoor est.) | 3.4 | 3.5 | 1 | 1 |
| 5101 | 99 | Data Analyst | Medly Pharmacy | Brooklyn, NY | $51K-$87K (Glassdoor est.) | $47K-$82K (Glassdoor est.) | 4.7 | 4.8 | 1 | 1 |
| 5108 | 105 | Data Analyst | Fund for Public Health | Long Island City, NY | $51K-$87K (Glassdoor est.) | $44K-$77K (Glassdoor est.) | 3.0 | 2.9 | 1 | 1 |
| 5104 | 106 | Data & Service Health Analyst | BlueVoyant | New York, NY | $51K-$87K (Glassdoor est.) | $44K-$77K (Glassdoor est.) | 4.2 | 3.9 | 1 | 1 |

Showing 10 of 123 rows.

## 02. Missing values disguised as -1 or Unknown

**Status:** FLAGGED · **Severity:** warning · **Rows returned:** 12

Columns where missing data is stored as a value instead of being empty.

Query: `data_quality/sql/02_hidden_missing_values.sql` · Full results: `reports/check_results/02_hidden_missing_values.csv`

| column_name | minus_one | blank | unknown_text | total_missing | pct_missing |
|---|---|---|---|---|---|
| easy_apply | 5468 | 0 | 0 | 5468 | 97.1 |
| competitors | 4328 | 0 | 0 | 4328 | 76.9 |
| revenue | 366 | 0 | 1452 | 1818 | 32.3 |
| founded | 1635 | 0 | 0 | 1635 | 29.0 |
| industry | 843 | 0 | 0 | 843 | 15.0 |
| sector | 843 | 0 | 0 | 843 | 15.0 |
| rating | 597 | 0 | 0 | 597 | 10.6 |
| size | 366 | 0 | 99 | 465 | 8.3 |
| type_of_ownership | 366 | 0 | 40 | 406 | 7.2 |
| headquarters | 384 | 0 | 0 | 384 | 6.8 |

Showing 10 of 12 rows.

## 03. Effect of -1 ratings on the average

**Status:** INFO · **Severity:** info · **Rows returned:** 1

How wrong a simple average becomes if -1 is treated as a real rating.

Query: `data_quality/sql/03_sentinel_impact_on_rating.sql` · Full results: `reports/check_results/03_sentinel_impact_on_rating.csv`

| total_rows | rows_with_rating_minus_one | naive_average_rating | correct_average_rating | error_in_naive_average |
|---|---|---|---|---|
| 5631 | 597 | 3.23 | 3.73 | 0.5 |

## 04. Salary values that are missing or in the wrong unit

**Status:** FLAGGED · **Severity:** error · **Rows returned:** 59

Salaries stored as -1, or hourly pay mixed into a column of annual salaries.

Query: `data_quality/sql/04_salary_format_issues.sql` · Full results: `reports/check_results/04_salary_format_issues.csv`

| row_id | job_title | company_name_clean | salary_estimate | issue |
|---|---|---|---|---|
| 4334 | Data Analyst, Product Insights | Alteryx | $65-$75Per Hour(Employer est.) | hourly rate mixed into annual salary column |
| 4335 | Data Analyst | Hospitality Training Academy | $65-$75Per Hour(Employer est.) | hourly rate mixed into annual salary column |
| 4336 | Data Analyst | EP Wealth Advisors | $65-$75Per Hour(Employer est.) | hourly rate mixed into annual salary column |
| 4337 | Data Analyst | The Trevor Project | $65-$75Per Hour(Employer est.) | hourly rate mixed into annual salary column |
| 4338 | Data Analyst | Vaco Technology | $65-$75Per Hour(Employer est.) | hourly rate mixed into annual salary column |
| 4339 | Data Analyst | Gilead Sciences | $65-$75Per Hour(Employer est.) | hourly rate mixed into annual salary column |
| 4340 | Data Analyst | Robert Half | $65-$75Per Hour(Employer est.) | hourly rate mixed into annual salary column |
| 4341 | Junior Data Analyst | Staffigo Technical Services, LLC | $65-$75Per Hour(Employer est.) | hourly rate mixed into annual salary column |
| 4342 | Data Analyst (Healthcare) | Themesoft Inc | $65-$75Per Hour(Employer est.) | hourly rate mixed into annual salary column |
| 4343 | Data Analyst | Arize Corporation | $65-$75Per Hour(Employer est.) | hourly rate mixed into annual salary column |

Showing 10 of 59 rows.

## 05. Company name field contaminated or empty

**Status:** FLAGGED · **Severity:** error · **Rows returned:** 5,036

Company names with the star rating glued on, or no name at all.

Query: `data_quality/sql/05_company_name_field_issues.sql` · Full results: `reports/check_results/05_company_name_field_issues.csv`

| row_id | company_name_raw | company_name_clean | rating | issue |
|---|---|---|---|---|
| 1 | Vera Institute of Justice\n3.2 | Vera Institute of Justice | 3.2 | rating appended to company name |
| 2 | Visiting Nurse Service of New York\n3.8 | Visiting Nurse Service of New York | 3.8 | rating appended to company name |
| 3 | Squarespace\n3.4 | Squarespace | 3.4 | rating appended to company name |
| 4 | Celerity\n4.1 | Celerity | 4.1 | rating appended to company name |
| 5 | FanDuel\n3.9 | FanDuel | 3.9 | rating appended to company name |
| 6 | Point72\n3.9 | Point72 | 3.9 | rating appended to company name |
| 7 | Two Sigma\n4.4 | Two Sigma | 4.4 | rating appended to company name |
| 8 | GNY Insurance Companies\n3.7 | GNY Insurance Companies | 3.7 | rating appended to company name |
| 9 | DMGT\n4.0 | DMGT | 4.0 | rating appended to company name |
| 10 | Riskified\n4.4 | Riskified | 4.4 | rating appended to company name |

Showing 10 of 5,036 rows.

## 06. Locations not in 'City, ST' format

**Status:** FLAGGED · **Severity:** warning · **Rows returned:** 31

Locations that cannot be mapped to a city, such as Remote or a state name.

Query: `data_quality/sql/06_location_format_issues.sql` · Full results: `reports/check_results/06_location_format_issues.csv`

| location | postings | issue |
|---|---|---|
| United States | 85 | not a city |
| Remote | 51 | not a city |
| New Jersey | 37 | state or region only, no city |
| Greenwood Village, Arapahoe, CO | 8 | extra part (county) in location |
| Ontario | 5 | state or region only, no city |
| California | 4 | state or region only, no city |
| Illinois | 4 | state or region only, no city |
| Connecticut | 3 | state or region only, no city |
| Mayfield Heights, Cuyahoga, OH | 3 | extra part (county) in location |
| North Carolina | 3 | state or region only, no city |

Showing 10 of 31 rows.

## 07. Same company under different names

**Status:** FLAGGED · **Severity:** warning · **Rows returned:** 155

Groups of names sharing headquarters, founding year, size and revenue. A list for a person to review.

Query: `data_quality/sql/07_company_name_variants.sql` · Full results: `reports/check_results/07_company_name_variants.csv`

| headquarters | founded_year | size | revenue | name_count | name_variants | postings_affected |
|---|---|---|---|---|---|---|
| New York, NY | 1784 | 10000+ employees | $10+ billion (USD) | 2 | The Bank of New York Mellon \| BNY Mellon | 19 |
| Saint Louis, MO | 1984 | 10000+ employees | $10+ billion (USD) | 2 | Centene Corporation \| Michigan Health Plan | 19 |
| Brentwood, TN | 2002 | 501 to 1000 employees | $500 million to $1 billion (USD) | 3 | Vaco \| Vaco Technology \| Vaco Staffing | 18 |
| Wayne, PA | 1970 | 1001 to 5000 employees | $100 to $500 million (USD) | 2 | The Judge Group, Inc. \| The Judge Group | 17 |
| New York, NY | 1799 | 10000+ employees | $10+ billion (USD) | 4 | JPMorgan Chase \| J.P. Morgan \| JPMorgan Chase & Co. \| JP… | 12 |
| New York, NY | 1985 | 201 to 500 employees | $25 to $50 million (USD) | 3 | RMS Computer Corporation \| RMS Computer \| RMS Computer Co… | 12 |
| Tokyo, Japan | 1967 | 10000+ employees | $10+ billion (USD) | 4 | NTT DATA \| NTT DATA Corporation \| NTT DATA Services \| NT… | 10 |
| Columbia, MD | 2001 | 201 to 500 employees | $50 to $100 million (USD) | 2 | Impaq International, Llc \| IMPAQ International, LLC | 9 |
| New York, NY | 1841 | 10000+ employees | $5 to $10 billion (USD) | 2 | NYU Langone Health \| NYU Langone | 9 |
| Reston, VA | 1969 | 10000+ employees | $10+ billion (USD) | 2 | Leidos Holdings Inc. \| Leidos | 9 |

Showing 10 of 155 rows.

## 08. Values outside valid ranges

**Status:** PASS · **Severity:** error · **Rows returned:** 0

Ratings outside 1 to 5, founding years after 2020, invalid flags or impossible salaries.

Query: `data_quality/sql/08_out_of_range_values.sql` · Full results: `reports/check_results/08_out_of_range_values.csv`

No rows returned.

## 09. Very old founding years to verify

**Status:** INFO · **Severity:** info · **Rows returned:** 28

Companies founded before 1800. Some are correct, some are not, so each needs checking against a source.

Query: `data_quality/sql/09_founded_year_review.sql` · Full results: `reports/check_results/09_founded_year_review.csv`

| company_name_clean | founded_year | headquarters | postings |
|---|---|---|---|
| City of New York | 1625 | New York, NY | 8 |
| City of Boston | 1630 | Boston, MA | 1 |
| EMD Millipore | 1668 | Boston, MA | 1 |
| Merck KGaA | 1668 | Darmstadt, Germany | 2 |
| University of California Berkeley | 1682 | Berkeley, CA | 1 |
| London Stock Exchange Group | 1698 | London, United Kingdom | 1 |
| City of Albuquerque | 1706 | Albuquerque, NM | 1 |
| University of Pennsylvania | 1740 | Philadelphia, PA | 5 |
| Rutgers University | 1766 | Piscataway, NJ | 1 |
| Molson Coors | 1774 | Chicago, IL | 1 |

Showing 10 of 28 rows.

## 10. Companies with an unusually large share of postings

**Status:** INFO · **Severity:** info · **Rows returned:** 8

Employers posting far more than others, which can skew any market-level number.

Query: `data_quality/sql/10_posting_concentration.sql` · Full results: `reports/check_results/10_posting_concentration.csv`

| company_rank | company_name_clean | postings | pct_of_all_postings | distinct_locations | average_rating |
|---|---|---|---|---|---|
| 1 | Staffigo Technical Services, LLC | 234 | 4.16 | 63 | 5.0 |
| 2 | Avacend, Inc. | 45 | 0.8 | 15 | 2.5 |
| 3 | Kforce | 41 | 0.73 | 25 | 4.1 |
| 4 | Diverse Lynx | 35 | 0.62 | 18 | 3.9 |
| 5 | Citi | 33 | 0.59 | 6 | 3.7 |
| 6 | Citibank | 32 | 0.57 | 5 | 3.75 |
| 6 | Robert Half | 32 | 0.57 | 24 | 3.5 |
| 8 | APN Software Services Inc. | 28 | 0.5 | 23 | 4.1 |

## 11. Same salary repeated across consecutive rows

**Status:** FLAGGED · **Severity:** error · **Rows returned:** 204

Runs of 10 or more consecutive rows from 8 or more different companies with an identical salary.

Query: `data_quality/sql/11_repeated_salary_blocks.sql` · Full results: `reports/check_results/11_repeated_salary_blocks.csv`

| salary_estimate | first_row_id | last_row_id | consecutive_rows | distinct_companies |
|---|---|---|---|---|
| $37K-$66K (Glassdoor est.) | 1 | 30 | 30 | 30 |
| $46K-$87K (Glassdoor est.) | 31 | 60 | 30 | 29 |
| $51K-$88K (Glassdoor est.) | 61 | 90 | 30 | 28 |
| $51K-$87K (Glassdoor est.) | 91 | 120 | 30 | 30 |
| $59K-$85K (Glassdoor est.) | 121 | 150 | 30 | 29 |
| $43K-$76K (Glassdoor est.) | 151 | 181 | 31 | 29 |
| $60K-$110K (Glassdoor est.) | 182 | 211 | 30 | 29 |
| $41K-$78K (Glassdoor est.) | 212 | 240 | 29 | 29 |
| $45K-$88K (Glassdoor est.) | 241 | 251 | 11 | 11 |
| $73K-$127K (Glassdoor est.) | 252 | 265 | 14 | 14 |

Showing 10 of 204 rows.
