# Data quality findings

**Dataset:** Glassdoor "Data Analyst" job postings for the United States, scraped in June 2020.
Published at [picklesueat/data_jobs_data](https://github.com/picklesueat/data_jobs_data) (MIT licence).
Pinned to commit `d3f96ca`. 5,631 rows, 15 columns.

**Method:** 11 SQL checks on SQLite, repeated independently in pandas. Both give the same results, and 17 automated tests confirm it. Full output is in [`reports/data_quality_report.md`](../reports/data_quality_report.md).

## Summary

| # | Finding | Rows affected | Severity |
|---|---|---|---|
| 1 | Salary is copied across each page of search results | 4,917 (87.3%) | High |
| 2 | Duplicate postings that an exact-match check cannot see | 123 (2.2%) | High |
| 3 | Missing values stored as `-1`, which corrupts averages | 12 of 15 columns | High |
| 4 | Company name field has the star rating glued onto it | 5,034 (89.4%) | Medium |
| 5 | Hourly pay mixed into an annual salary column | 13 | Medium |
| 6 | The same company appears under several names | 155 groups to review | Medium |
| 7 | Locations that cannot be mapped to a city | 235 (4.2%) | Low |

Not every check found a problem. Ratings, founding years, flags and parsed salaries all stayed inside valid ranges (check 08 returned zero rows). That matters too: it shows the problems are about meaning and structure, not obviously broken values.

---

## 1. Salary is copied across each page of search results

**What I found.** The same salary repeats for long runs of consecutive rows from unrelated companies. Rows 1 to 30 all show `$37K-$66K`, including a *Senior* Data Analyst and an *Entry Level* Data Analyst. The value changes exactly at row 31, then again at row 61, and so on. Check 11 finds 204 such blocks covering 4,917 rows.

**Why it happens.** Blocks of 30 match one page of Glassdoor results. The scraper's salary selector searches the whole page instead of the selected job, so it most likely reads the first salary on the page each time. Full details are in the [bug report](BUG_REPORT.md).

**Why it matters.** This is the most serious issue because nothing looks wrong. Every value is well formatted and believable. Only a check on the *pattern* across rows exposes it.

**Fix or prevent.** Scope the selector to the job's own panel and re-collect salaries. Until then, label the column as unreliable. Keep check 11 in the release pipeline.

## 2. Duplicate postings that an exact-match check cannot see

**What I found.** 122 postings were collected more than once, leaving 123 extra copies (2.2% of rows). A normal duplicate check on the raw fields finds **zero** of them. The copies were collected at different times, and the company field changed between collections: `Bosch Group\n4.1` in row 737 and `Bosch Group\n4.0` in row 2262. A few copies also differ only in blank lines inside the description.

In 121 of the 123 extra copies the rating differs from the first copy, and in 106 the salary differs (a side effect of finding 1). So the dataset gives two different answers about the same job.

**Why it matters.** Duplicates inflate posting counts, which is the core metric for any hiring trend. Conflicting values make it unclear which copy to trust.

**Fix or prevent.** Deduplicate on a stable posting ID from the source, which this scrape did not keep. Without one, use the normalised key from check 01: lower-case title, cleaned company name, location and whitespace-normalised description. When copies disagree, keep the most recent one and log the conflict.

## 3. Missing values stored as `-1`

**What I found.** 12 of 15 columns use `-1` (and sometimes `Unknown`) to mean "missing". Examples: `easy_apply` (97.1%), `competitors` (76.9%), `founded` (29.0%), `rating` (10.6%).

The effect on numbers is real. Averaging the `rating` column as stored gives **3.23**. Treating `-1` as missing gives **3.73**. The simple calculation is off by half a star.

**Fix or prevent.** Store missing values as `NULL` at load time. Add a schema rule that rejects `-1` in numeric columns where it is not a valid value. For `easy_apply`, `-1` really means "No", so convert it to a true/false column.

## 4. Company name field has the star rating glued onto it

**What I found.** 5,034 company names end with a line break and the rating, for example `Squarespace\n3.4`. 2 more are empty. This is the root cause of finding 2: when the rating changes, the "same" company looks like a different one.

**Fix or prevent.** Split the field at the line break during loading and keep the rating only in the `rating` column. Add a test that no company name contains a line break.

## 5. Hourly pay mixed into an annual salary column

**What I found.** 13 rows hold an hourly rate (`$65-$75 Per Hour`) in a column where everything else is an annual figure in thousands. Read as annual, these look like $65K to $75K a year, roughly half the true value. All 13 come from 13 different employers but show the identical rate, so they are probably affected by finding 1 too. 46 more rows have no salary at all (stored as `-1`).

**Fix or prevent.** Add a `pay_period` column and convert everything to one unit. Reject any salary text the parser does not recognise instead of loading it silently.

## 6. The same company appears under several names

**What I found.** Grouping by headquarters, founding year, size and revenue finds 155 groups with more than one name. Real examples: `JPMorgan Chase`, `J.P. Morgan`, `JPMorgan Chase & Co.` and `JPMorgan Chase Bank, N.A.`; `BNY Mellon` and `The Bank of New York Mellon`; `NTT DATA` with four spellings.

This check also returns false alarms, such as `QuinStreet` and `Qualys`, which share those attributes but are different companies. So it is a review list for a person, not an automatic merge rule.

**Why it matters.** Counting postings per company splits one employer into several smaller ones. For a workforce data company, mapping names to the right company is part of the product.

**Fix or prevent.** Keep a company reference table with one ID per company and known aliases. Map every posting to an ID during loading and send unknown names to a review queue.

## 7. Locations that cannot be mapped to a city

**What I found.** 235 rows do not follow `City, ST`. 136 say `Remote` or `United States`, 82 give only a state or province (`New Jersey`, `Ontario`), 16 include a county (`Greenwood Village, Arapahoe, CO`), and 1 says `Multiple Locations, Multiple Locations`.

**Fix or prevent.** Map locations to a standard geography with an explicit `remote` flag, and report the share of unmapped rows in every release.

---

## Things that looked wrong but need checking first

**Very old founding years.** Check 09 lists 28 companies founded before 1800. `City of New York` with 1625 is correct (New Amsterdam). `University of California Berkeley` with 1682 is almost certainly wrong, since the university was founded in 1868. The lesson: a suspicious value is a question, not a bug, until it is checked against a source.

**One employer posts far more than anyone else.** Staffigo Technical Services posted 234 jobs (4.2% of all rows) across 63 locations, and every one carries a 5.0 rating. That could be a genuine staffing agency, or repeated listings. It is worth knowing before using this data for market-level numbers.

## How I would prevent these issues in a pipeline

1. **Validate on load.** Convert `-1` to `NULL`, split combined fields, and reject unparseable values instead of storing them.
2. **Run the checks automatically.** `run_checks.py --fail-on-error` exits with an error when an error-level check finds problems, so it can block a release in CI.
3. **Agree on "correct" with the data team.** For each column, write down the allowed values, the unit and what missing looks like.
4. **Compare releases.** Track row counts, duplicate rate and missing-value rates per release, and alert on sudden changes.
5. **Test the checks themselves.** The test suite inserts known-bad rows and confirms each check catches them, so a broken check cannot pass silently.
