import csv
import sqlite3
import sys
from pathlib import Path

from download_dataset import CSV_PATH

DB_PATH = Path(__file__).parent / "data" / "job_postings.db"
TABLE = "job_postings"

csv.field_size_limit(10_000_000)


def normalise_header(name):
    cleaned = "".join(char.lower() if char.isalnum() else "_" for char in name.strip())
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_")


def load(csv_path=CSV_PATH, db_path=DB_PATH):
    with open(csv_path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        headers = [normalise_header(name) for name in next(reader)]
        rows = [row + [""] * (len(headers) - len(row)) for row in reader]

    db_path.unlink(missing_ok=True)
    with sqlite3.connect(db_path) as connection:
        columns = ", ".join(f'"{name}" TEXT' for name in headers)
        connection.execute(f"CREATE TABLE {TABLE} (row_id INTEGER PRIMARY KEY, {columns})")
        placeholders = ", ".join("?" for _ in headers)
        quoted = ", ".join(f'"{name}"' for name in headers)
        connection.executemany(f"INSERT INTO {TABLE} ({quoted}) VALUES ({placeholders})", rows)
    return len(rows), headers


def main():
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else CSV_PATH
    count, headers = load(csv_path)
    print(f"Loaded {count:,} rows and {len(headers)} columns into {DB_PATH} (table: {TABLE})")


if __name__ == "__main__":
    main()
