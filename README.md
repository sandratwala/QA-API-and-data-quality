# QA project: API tests and data quality checks

![QA checks](https://github.com/YOUR-USERNAME/qa-api-and-data-quality/actions/workflows/tests.yml/badge.svg)

A two-part testing project:

1. **API testing:** a pytest suite of 28 tests against the public [JSONPlaceholder](https://jsonplaceholder.typicode.com) API, covering successful requests, invalid input and edge cases.
2. **Data quality testing:** 11 SQL checks on 5,631 real Glassdoor job postings, repeated in pandas and verified by 17 automated tests.

Both parts run automatically on every push with GitHub Actions.

## Headline findings

The data checks found seven real problems in a public job postings dataset. The three most important:

- **87% of salaries are not the job's own salary.** The same salary repeats for every job on a page of search results, because the scraper read the salary from the wrong part of the page. See the [bug report](docs/BUG_REPORT.md).
- **123 duplicate postings that a normal duplicate check finds zero of,** because the company's star rating is glued onto its name and changed between scrapes.
- **Missing values stored as `-1` make the average company rating 3.23 instead of 3.73.**

Full write-up: [docs/FINDINGS.md](docs/FINDINGS.md). Full check output: [reports/data_quality_report.md](reports/data_quality_report.md).

## Project structure

```
qa-api-and-data-quality/
├── tests/
│   ├── api/
│   │   ├── conftest.py                 shared API client with timeout and retries
│   │   └── test_posts_api.py           28 API tests
│   └── data/
│       ├── conftest.py                 fixtures that download and load the dataset
│       └── test_data_quality_checks.py 17 tests that verify the data checks
├── data_quality/
│   ├── download_dataset.py             downloads the pinned dataset and verifies its checksum
│   ├── load_to_sqlite.py               loads the raw CSV into SQLite without changing it
│   ├── run_checks.py                   runs every SQL check and writes the report
│   ├── pandas_checks.py                the same checks written in pandas
│   └── sql/                            one file per check
├── reports/
│   ├── data_quality_report.md          latest check results
│   └── check_results/                  full results of each check as CSV
├── docs/
│   ├── FINDINGS.md                     what the data checks found and how to fix it
│   ├── BUG_REPORT.md                   sample bug report
│   └── TEST_PLAN.md                    test plan for the API suite
├── .github/workflows/tests.yml         runs everything on GitHub Actions
└── pyproject.toml                      dependencies and pytest settings
```

## How to run it

You need Python 3.10 or newer and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/YOUR-USERNAME/qa-api-and-data-quality.git
cd qa-api-and-data-quality
uv sync
```

### Part 1: API tests

```bash
uv run pytest tests/api
```

Run one group of tests with a marker:

```bash
uv run pytest tests/api -m negative
uv run pytest tests/api -m edge
```

Expected result: all tests pass, and the 3 tests marked `known_bug` show as `XFAIL`. Those tests describe how the API *should* behave and are expected to fail until the bug is fixed.

### Part 2: data quality checks

```bash
uv run python data_quality/run_checks.py
```

This downloads the dataset (about 19 MB) the first time, checks its SHA-256 checksum, loads it into SQLite and runs all 11 checks. It prints a summary and writes `reports/data_quality_report.md`.

To use the checks as a release gate, add `--fail-on-error`. The script then exits with code 1 if any error-level check finds a problem:

```bash
uv run python data_quality/run_checks.py --fail-on-error
```

Run the pandas version and the tests that compare both versions:

```bash
uv run python data_quality/pandas_checks.py
uv run pytest tests/data
```

To explore the data yourself, open `data_quality/data/job_postings.db` in [DB Browser for SQLite](https://sqlitebrowser.org), run `data_quality/sql/00_create_views.sql` first, then any check file.

### Everything at once

```bash
uv run pytest
```

Without uv, use `pip install pytest requests pandas` and run the same commands without `uv run`.

## The dataset

| | |
|---|---|
| Name | Glassdoor Data Analyst job postings, United States, June 2020 |
| Source | [picklesueat/data_jobs_data](https://github.com/picklesueat/data_jobs_data), `data/DataAnalyst.csv` (MIT licence) |
| Version | commit `d3f96ca2ff315d29af944bb72f1abeee048cd176` |
| SHA-256 | `a0807411e5d58438e5fed830aad8a624f7676d140894e8b50871d8a5a86f617a` |
| Size | 5,631 rows, 15 columns |

The download is pinned to one commit and verified by checksum, so everyone runs the checks on exactly the same file. The raw data is loaded as text without any cleaning, so the checks see the data exactly as published.

## The data checks

| # | Check | Severity | SQL used |
|---|---|---|---|
| 01 | Duplicate postings after normalising company name, case and whitespace | error | window functions (`ROW_NUMBER`, `FIRST_VALUE`) |
| 02 | Missing values stored as `-1`, blank or `Unknown`, per column | warning | `UNION ALL`, aggregation |
| 03 | How much `-1` ratings distort the average rating | info | aggregation |
| 04 | Salaries that are missing, hourly, or cannot be parsed | error | `CASE`, string parsing |
| 05 | Company names with the rating appended, or empty | error | string functions |
| 06 | Locations not in `City, ST` format | warning | `GLOB` pattern, `GROUP BY` |
| 07 | The same company under different names | warning | CTEs, `GROUP_CONCAT`, join |
| 08 | Ratings, years, flags and salaries outside valid ranges | error | `UNION ALL` of rules |
| 09 | Founding years before 1800, for manual review | info | aggregation |
| 10 | Companies with an unusually large share of postings | info | window functions (`SUM OVER`, `RANK`) |
| 11 | The same salary repeated across consecutive rows | error | gaps-and-islands with `ROW_NUMBER` |

All checks read from one view, `postings_normalized` (`sql/00_create_views.sql`), which cleans the messy fields once so every check uses the same rules.

### How the checks are tested

A data check can be wrong too, so the tests in `tests/data` check the checks:

- **Two independent versions agree.** Every check is written in SQL and again in pandas, and the tests confirm both return the same rows.
- **Injected problems are caught.** Tests build a small database with known-bad rows, such as a rating of 7.5 or a salary of `$90K-$60K`, and confirm the right check flags exactly those rows.
- **Clean data passes.** A set of valid rows must pass every error-level check, so the checks do not raise false alarms.
- **Known findings stay found.** For example, the duplicate pair in rows 737 and 2262 must always be caught.

## The API tests

See the [test plan](docs/TEST_PLAN.md) for the full approach. In short:

| Group | Examples |
|---|---|
| Successful requests | list and fetch posts, check fields and types, filter by user, create, replace, update and delete |
| Invalid input | unknown IDs (`0`, `-1`, `101`, `abc`), unknown routes |
| Edge cases | Unicode and emoji, a 10,000-character title, injection strings, filters with no matches, limits above the total |
| Known bugs | empty or wrongly typed payloads are accepted, marked `xfail` with a bug ID |

## Continuous integration

`.github/workflows/tests.yml` runs on every push and pull request, and every Monday at 06:00 UTC to catch changes in the public API. It has two jobs:

- **api-tests** runs the API suite and saves the results as JUnit XML.
- **data-quality** runs the SQL checks, the pandas checks and the data tests, then uploads the report as an artifact.
