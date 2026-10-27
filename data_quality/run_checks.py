import argparse
import csv
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from download_dataset import CSV_PATH, download
from load_to_sqlite import DB_PATH, load

ROOT = Path(__file__).resolve().parent.parent
SQL_DIR = Path(__file__).parent / "sql"
REPORT_DIR = ROOT / "reports"
RESULTS_DIR = REPORT_DIR / "check_results"
REPORT_PATH = REPORT_DIR / "data_quality_report.md"
PREVIEW_ROWS = 10


@dataclass(frozen=True)
class Check:
    sql_file: str
    title: str
    severity: str
    meaning: str


CHECKS = [
    Check("01_duplicate_postings.sql", "Duplicate postings hidden by a changing company field", "error",
          "Same title, company, location and description appear more than once. Each row listed is an extra copy."),
    Check("02_hidden_missing_values.sql", "Missing values disguised as -1 or Unknown", "warning",
          "Columns where missing data is stored as a value instead of being empty."),
    Check("03_sentinel_impact_on_rating.sql", "Effect of -1 ratings on the average", "info",
          "How wrong a simple average becomes if -1 is treated as a real rating."),
    Check("04_salary_format_issues.sql", "Salary values that are missing or in the wrong unit", "error",
          "Salaries stored as -1, or hourly pay mixed into a column of annual salaries."),
    Check("05_company_name_field_issues.sql", "Company name field contaminated or empty", "error",
          "Company names with the star rating glued on, or no name at all."),
    Check("06_location_format_issues.sql", "Locations not in 'City, ST' format", "warning",
          "Locations that cannot be mapped to a city, such as Remote or a state name."),
    Check("07_company_name_variants.sql", "Same company under different names", "warning",
          "Groups of names sharing headquarters, founding year, size and revenue. A list for a person to review."),
    Check("08_out_of_range_values.sql", "Values outside valid ranges", "error",
          "Ratings outside 1 to 5, founding years after 2020, invalid flags or impossible salaries."),
    Check("09_founded_year_review.sql", "Very old founding years to verify", "info",
          "Companies founded before 1800. Some are correct, some are not, so each needs checking against a source."),
    Check("10_posting_concentration.sql", "Companies with an unusually large share of postings", "info",
          "Employers posting far more than others, which can skew any market-level number."),
    Check("11_repeated_salary_blocks.sql", "Same salary repeated across consecutive rows", "error",
          "Runs of 10 or more consecutive rows from 8 or more different companies with an identical salary."),
]


def connect(db_path=DB_PATH):
    connection = sqlite3.connect(db_path)
    connection.executescript((SQL_DIR / "00_create_views.sql").read_text(encoding="utf-8"))
    return connection


def run_check(connection, check):
    cursor = connection.execute((SQL_DIR / check.sql_file).read_text(encoding="utf-8"))
    columns = [description[0] for description in cursor.description]
    return columns, cursor.fetchall()


def status_for(check, rows):
    if check.severity == "info":
        return "INFO"
    return "FLAGGED" if rows else "PASS"


def format_cell(value, limit=60):
    text = "" if value is None else str(value).replace("|", "\\|").replace("\n", " ")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def markdown_table(columns, rows):
    lines = ["| " + " | ".join(columns) + " |", "|" + "---|" * len(columns)]
    lines += ["| " + " | ".join(format_cell(value) for value in row) + " |" for row in rows]
    return "\n".join(lines)


def save_csv(check, columns, rows):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / check.sql_file.replace(".sql", ".csv")
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)
    return path


def write_report(results, row_count):
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Data quality report",
        "",
        f"Dataset: Glassdoor Data Analyst job postings, {row_count:,} rows. Generated {generated}.",
        "",
        "| # | Check | Severity | Status | Rows returned |",
        "|---|---|---|---|---|",
    ]
    for check, status, columns, rows in results:
        number = check.sql_file[:2]
        lines.append(f"| {number} | {check.title} | {check.severity} | {status} | {len(rows):,} |")

    for check, status, columns, rows in results:
        lines += [
            "",
            f"## {check.sql_file[:2]}. {check.title}",
            "",
            f"**Status:** {status} · **Severity:** {check.severity} · **Rows returned:** {len(rows):,}",
            "",
            check.meaning,
            "",
            f"Query: `data_quality/sql/{check.sql_file}` · Full results: "
            f"`reports/check_results/{check.sql_file.replace('.sql', '.csv')}`",
            "",
        ]
        if rows:
            preview = rows[:PREVIEW_ROWS]
            lines.append(markdown_table(columns, preview))
            if len(rows) > PREVIEW_ROWS:
                lines += ["", f"Showing {PREVIEW_ROWS} of {len(rows):,} rows."]
        else:
            lines.append("No rows returned.")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare_database():
    download()
    if not DB_PATH.exists():
        load(CSV_PATH, DB_PATH)


def main():
    parser = argparse.ArgumentParser(description="Run SQL data quality checks on the job postings dataset.")
    parser.add_argument("--fail-on-error", action="store_true",
                        help="exit with code 1 if any error-level check finds problems (use as a release gate)")
    args = parser.parse_args()

    prepare_database()
    connection = connect()
    row_count = connection.execute("SELECT COUNT(*) FROM job_postings").fetchone()[0]

    results = []
    for check in CHECKS:
        columns, rows = run_check(connection, check)
        save_csv(check, columns, rows)
        results.append((check, status_for(check, rows), columns, rows))
    connection.close()

    write_report(results, row_count)

    print(f"\n{'#':<3} {'Check':<55} {'Severity':<9} {'Status':<8} {'Rows':>6}")
    for check, status, columns, rows in results:
        print(f"{check.sql_file[:2]:<3} {check.title[:54]:<55} {check.severity:<9} {status:<8} {len(rows):>6,}")
    print(f"\nReport written to {REPORT_PATH.relative_to(ROOT)}")

    failed = [check for check, status, _, _ in results if check.severity == "error" and status == "FLAGGED"]
    if args.fail_on_error and failed:
        print(f"Release gate failed: {len(failed)} error-level checks found problems.")
        sys.exit(1)


if __name__ == "__main__":
    main()
