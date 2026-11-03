import csv

import pytest

import pandas_checks
import run_checks
from download_dataset import EXPECTED_SHA256, sha256_of

pytestmark = pytest.mark.data

MINIMUM_ROWS = 500


def row_ids(result, column="row_id"):
    columns, rows = result
    index = columns.index(column)
    return {row[index] for row in rows}


def check_by_number(number):
    return next(check for check in run_checks.CHECKS if check.sql_file.startswith(number))


class TestDatasetIntegrity:
    def test_downloaded_file_matches_pinned_checksum(self, csv_path):
        assert sha256_of(csv_path) == EXPECTED_SHA256

    def test_dataset_has_enough_rows(self, frame):
        assert len(frame) >= MINIMUM_ROWS

    def test_every_csv_row_is_loaded_into_sqlite(self, csv_path, connection):
        csv.field_size_limit(10_000_000)
        with open(csv_path, newline="", encoding="utf-8-sig") as handle:
            csv_rows = sum(1 for _ in csv.reader(handle)) - 1

        db_rows = connection.execute("SELECT COUNT(*) FROM job_postings").fetchone()[0]

        assert db_rows == csv_rows


class TestSqlAndPandasAgree:
    def test_duplicate_postings(self, sql_results, frame):
        assert row_ids(sql_results["01"]) == pandas_checks.duplicate_postings(frame)

    def test_hidden_missing_values(self, sql_results, frame):
        columns, rows = sql_results["02"]
        sql_counts = {row[0]: row[columns.index("total_missing")] for row in rows}

        assert sql_counts == pandas_checks.hidden_missing_counts(frame)

    def test_salary_format_issues(self, sql_results, frame):
        assert row_ids(sql_results["04"]) == pandas_checks.salary_format_issues(frame)

    def test_company_name_issues(self, sql_results, frame):
        assert row_ids(sql_results["05"]) == pandas_checks.company_name_issues(frame)

    def test_location_format_issues(self, sql_results, frame):
        columns, rows = sql_results["06"]
        sql_total = sum(row[columns.index("postings")] for row in rows)

        assert sql_total == len(pandas_checks.location_format_issues(frame))

    def test_out_of_range_values(self, sql_results, frame):
        assert row_ids(sql_results["08"]) == pandas_checks.out_of_range_values(frame)

    def test_repeated_salary_blocks(self, sql_results, frame):
        columns, rows = sql_results["11"]
        first, last = columns.index("first_row_id"), columns.index("last_row_id")
        sql_blocks = {(row[first], row[last]) for row in rows}

        assert sql_blocks == pandas_checks.repeated_salary_blocks(frame)


class TestKnownFindings:
    def test_known_duplicate_pair_is_caught(self, sql_results):
        columns, rows = sql_results["01"]
        pairs = {(row[columns.index("row_id")], row[columns.index("duplicate_of_row_id")]) for row in rows}

        assert (2262, 737) in pairs

    def test_matching_on_raw_fields_misses_almost_every_duplicate(self, sql_results, frame):
        raw_matches = pandas_checks.exact_duplicates_on_raw_fields(frame)
        normalised_matches = row_ids(sql_results["01"])

        assert len(raw_matches) < len(normalised_matches) / 10

    def test_correct_old_founding_year_goes_to_review_not_to_errors(self, sql_results):
        review = {row[0] for row in sql_results["09"][1]}

        assert "City of New York" in review
        assert sql_results["08"][1] == []


class TestChecksCatchInjectedProblems:
    def test_out_of_range_check_flags_bad_values(self, make_database, valid_row):
        connection = make_database(
            [
                valid_row,
                {**valid_row, "rating": "7.5"},
                {**valid_row, "founded": "2031"},
                {**valid_row, "easy_apply": "Maybe"},
                {**valid_row, "salary_estimate": "$900K-$950K (Glassdoor est.)"},
            ]
        )

        flagged = row_ids(run_checks.run_check(connection, check_by_number("08")))

        assert flagged == {2, 3, 4, 5}

    def test_duplicate_check_ignores_rating_and_whitespace_changes(self, make_database, valid_row):
        connection = make_database(
            [
                valid_row,
                {**valid_row, "company_name": "Example Co\n3.9", "job_description": "Analyse   hiring\n\ndata."},
                {**valid_row, "location": "Dallas, TX"},
            ]
        )

        flagged = row_ids(run_checks.run_check(connection, check_by_number("01")))

        assert flagged == {2}

    def test_salary_check_flags_hourly_and_missing_pay(self, make_database, valid_row):
        connection = make_database(
            [
                valid_row,
                {**valid_row, "salary_estimate": "$65-$75Per Hour(Employer est.)"},
                {**valid_row, "salary_estimate": "-1"},
                {**valid_row, "salary_estimate": "$90K-$60K (Glassdoor est.)"},
            ]
        )

        flagged = row_ids(run_checks.run_check(connection, check_by_number("04")))

        assert flagged == {2, 3, 4}

    def test_clean_data_passes_every_error_check(self, make_database, valid_row):
        rows = [
            {**valid_row, "company_name": f"Company {number}", "salary_estimate": f"${40 + number}K-$90K"}
            for number in range(12)
        ]
        connection = make_database(rows)

        for check in run_checks.CHECKS:
            if check.severity == "error":
                assert run_checks.run_check(connection, check)[1] == [], check.title
