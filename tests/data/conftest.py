import sqlite3

import pytest

import pandas_checks
import run_checks
from download_dataset import download
from load_to_sqlite import DB_PATH, TABLE, load


@pytest.fixture(scope="session")
def csv_path():
    return download()


@pytest.fixture(scope="session")
def connection(csv_path):
    load(csv_path, DB_PATH)
    connection = run_checks.connect(DB_PATH)
    yield connection
    connection.close()


@pytest.fixture(scope="session")
def frame(csv_path):
    return pandas_checks.load_postings(csv_path)


@pytest.fixture(scope="session")
def sql_results(connection):
    return {check.sql_file[:2]: run_checks.run_check(connection, check) for check in run_checks.CHECKS}


@pytest.fixture
def make_database(tmp_path):
    def build(rows):
        path = tmp_path / "injected.db"
        with sqlite3.connect(DB_PATH) as source:
            columns = [row[1] for row in source.execute(f"PRAGMA table_info({TABLE})") if row[1] != "row_id"]
        with sqlite3.connect(path) as target:
            column_sql = ", ".join(f'"{name}" TEXT' for name in columns)
            target.execute(f"CREATE TABLE {TABLE} (row_id INTEGER PRIMARY KEY, {column_sql})")
            for row in rows:
                values = [row.get(name, "") for name in columns]
                target.execute(
                    f"INSERT INTO {TABLE} ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})",
                    values,
                )
        return run_checks.connect(path)

    return build


@pytest.fixture
def valid_row():
    return {
        "job_title": "Data Analyst",
        "salary_estimate": "$50K-$80K (Glassdoor est.)",
        "job_description": "Analyse hiring data.",
        "rating": "4.0",
        "company_name": "Example Co\n4.0",
        "location": "Austin, TX",
        "headquarters": "Austin, TX",
        "size": "51 to 200 employees",
        "founded": "2010",
        "type_of_ownership": "Company - Private",
        "industry": "Internet",
        "sector": "Information Technology",
        "revenue": "$10 to $25 million (USD)",
        "competitors": "-1",
        "easy_apply": "-1",
    }
