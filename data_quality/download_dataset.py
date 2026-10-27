import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

SOURCE_REPO = "https://github.com/picklesueat/data_jobs_data"
PINNED_COMMIT = "d3f96ca2ff315d29af944bb72f1abeee048cd176"
CSV_URL = f"https://raw.githubusercontent.com/picklesueat/data_jobs_data/{PINNED_COMMIT}/data/DataAnalyst.csv"
EXPECTED_SHA256 = "a0807411e5d58438e5fed830aad8a624f7676d140894e8b50871d8a5a86f617a"

RAW_DIR = Path(__file__).parent / "data" / "raw"
CSV_PATH = RAW_DIR / "glassdoor_data_analyst_jobs.csv"
METADATA_PATH = RAW_DIR / "metadata.json"


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_valid_copy(path):
    return path.exists() and sha256_of(path) == EXPECTED_SHA256


def download():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if is_valid_copy(CSV_PATH):
        print(f"Dataset already downloaded and verified: {CSV_PATH}")
        return CSV_PATH

    response = requests.get(CSV_URL, timeout=120)
    response.raise_for_status()
    CSV_PATH.write_bytes(response.content)

    actual = sha256_of(CSV_PATH)
    if actual != EXPECTED_SHA256:
        CSV_PATH.unlink()
        sys.exit(f"Checksum mismatch: expected {EXPECTED_SHA256}, got {actual}. The file was deleted.")

    metadata = {
        "dataset": "Glassdoor Data Analyst job postings (United States, scraped June 2020)",
        "source_repository": SOURCE_REPO,
        "pinned_commit": PINNED_COMMIT,
        "download_url": CSV_URL,
        "sha256": actual,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Downloaded and verified {CSV_PATH} ({CSV_PATH.stat().st_size:,} bytes)")
    return CSV_PATH


if __name__ == "__main__":
    download()
