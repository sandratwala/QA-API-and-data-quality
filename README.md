# QA project: API tests and data quality checks

![QA checks](https://github.com/sandratwala/QA-API-and-data-quality/actions/workflows/tests.yml/badge.svg)

I built this to practise two sides of QA: testing an API, and testing data.

For the API part, I wrote pytest tests against [JSONPlaceholder](https://jsonplaceholder.typicode.com), a free practice API. The tests cover normal requests, bad input and edge cases like emoji, very long text and injection strings.

For the data part, I took a real dataset of 5,631 Glassdoor job postings and wrote SQL checks to see how trustworthy it is. I also wrote the same checks in pandas, so I could compare the two and make sure my checks were right.

## What I found

The biggest problem was the salaries. Every job on the same page of search results has the same salary, so a senior role and an entry level role both show $37K to $66K. That affects about 87% of the rows. I looked at the scraper's code and the salary was being read from the wrong part of the page. I wrote this up as a [bug report](docs/BUG_REPORT.md).

I also found 123 duplicate postings that a normal duplicate check doesn't catch. The company's rating is stuck to the end of its name (like `Bosch Group 4.1`), and it changed between scrapes, so the same job looks like two different ones.

Missing values are saved as `-1` instead of being left empty. If you average the ratings as they are, you get 3.23. If you treat `-1` as missing, you get 3.73.

There are a few smaller issues too, like hourly pay mixed in with yearly salaries and the same company spelled several ways. Everything is in [FINDINGS.md](docs/FINDINGS.md).

## Running it

You need Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/sandratwala/QA-API-and-data-quality.git
cd QA-API-and-data-quality
uv sync
uv run pytest
```

That runs all the tests. Three of the API tests show as `XFAIL` on purpose. They describe how the API should behave, and they'll keep failing until those bugs are fixed.

To run the data checks and get a report:

```bash
uv run python data_quality/run_checks.py
```

The dataset downloads by itself the first time (about 19 MB), and the script checks its checksum so it's always the same file. Results go to `reports/data_quality_report.md`.

If you add `--fail-on-error`, the script stops with an error when a serious check fails. That's how you'd use it to block a release.

For linting and formatting I use Ruff:

```bash
uv run ruff check .
uv run ruff format .
```

## How I checked my checks

A data check can be wrong too, so I didn't want to just trust mine. The tests in `tests/data` make sure the SQL and pandas versions give the same answer. They also add rows I know are bad (like a rating of 7.5) and check that the right check catches them, and they make sure clean data doesn't set anything off.

## The data

The dataset comes from [picklesueat/data_jobs_data](https://github.com/picklesueat/data_jobs_data) (MIT licence). It's Data Analyst job postings in the US, scraped in June 2020. I pinned it to commit `d3f96ca` so everyone tests the same file.

## Where things are

- `tests/api` has the API tests, and [TEST_PLAN.md](docs/TEST_PLAN.md) explains the approach
- `tests/data` has the tests for the data checks
- `data_quality/sql` has one SQL file per check
- `reports` has the latest results
- `docs` has the findings, bug report and test plan

GitHub Actions runs linting, the API tests and the data checks on every push, and once a week in case the public API changes.