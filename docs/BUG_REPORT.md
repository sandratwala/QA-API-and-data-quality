# BUG-DATA-01: Salary estimate is copied across every job on a results page

| Field | Value |
|---|---|
| Severity | High: salary data is wrong for most rows, and the error is invisible without a targeted check |
| Priority | P1: fix before any salary figure from this dataset is published or shared with customers |
| Component | Scraper (`glass_scraper.py`, function `collect_listing_info`) and the resulting `DataAnalyst.csv` |
| Dataset version | `picklesueat/data_jobs_data` at commit `d3f96ca`, SHA-256 `a0807411…f617a` |
| Found by | Check 11 (`data_quality/sql/11_repeated_salary_blocks.sql`) |
| Reporter | Sandra Twala |
| Status | Open |

## Summary

The `Salary Estimate` value does not belong to the individual job. The same salary repeats for blocks of up to 30 consecutive postings from different companies and seniority levels, which matches one page of search results. 4,917 of 5,631 rows (87.3%) sit inside one of these blocks.

## Steps to reproduce

1. Run `uv run python data_quality/download_dataset.py` to download the pinned dataset.
2. Run `uv run python data_quality/load_to_sqlite.py`.
3. Run this query on `data_quality/data/job_postings.db`:

   ```sql
   SELECT row_id, job_title, location, salary_estimate
   FROM job_postings
   WHERE row_id BETWEEN 1 AND 32;
   ```

4. Compare the salary for rows 1 to 30 with rows 31 and 32.

## Expected result

Each posting has its own salary estimate. Postings for different companies and seniority levels have different salaries.

## Actual result

Rows 1 to 30 all show `$37K-$66K (Glassdoor est.)`. This includes very different jobs:

| row_id | Job title | Company | Salary |
|---|---|---|---|
| 3 | Senior Data Analyst, Insights & Analytics Team | Squarespace | $37K-$66K |
| 29 | Data Analyst Entry Level | Endai | $37K-$66K |
| 31 | Data Analyst | Revel | $46K-$87K |

The value changes exactly at row 31, where the next page starts. Across the file, check 11 finds 204 blocks like this.

The same bug explains a second finding: 106 of the 123 extra copies found by check 01 have a different salary from the first copy, because each copy was collected from a different results page.

## Likely root cause

In `glass_scraper.py`, line 163 reads the salary with:

```python
driver.find_element_by_xpath('.//span[@class="gray salary"]').text
```

The XPath starts from the whole page, not from the selected job's detail panel. `find_element` returns the first match, so it most likely picks up the salary shown on the first job card of the results list, which stays the same until the scraper moves to the next page.

## Impact

- Any salary analysis by company, job title or seniority built on this column is unreliable.
- Average salaries are weighted by search page, not by job.
- The error passes every simple validity check: the values are well formed and in a believable range.

## Suggested fix

1. Scope the selector to the job detail panel, so the salary is read from the job that was clicked.
2. Re-collect salary for the affected rows, or mark the column as unreliable until then.
3. Add check 11 to the release pipeline with `--fail-on-error`, so a repeat of this pattern blocks the release.

## How to verify the fix

- Check 11 returns zero blocks.
- A manual spot check of 20 random postings against the live listing shows matching salaries.
- Duplicate copies of the same job (check 01) show the same salary.

## Attachments

- `reports/check_results/11_repeated_salary_blocks.csv`: all 204 blocks with first and last row
- `reports/data_quality_report.md`, section 11
