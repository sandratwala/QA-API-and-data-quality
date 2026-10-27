import re

import pandas as pd

from download_dataset import CSV_PATH, download

MISSING_MARKERS = {
    "rating": {"-1", "-1.0"},
    "company_name": set(),
    "salary_estimate": {"-1"},
    "headquarters": {"-1"},
    "size": {"-1", "Unknown"},
    "founded": {"-1"},
    "type_of_ownership": {"-1", "Unknown"},
    "industry": {"-1"},
    "sector": {"-1"},
    "revenue": {"-1"},
    "competitors": {"-1"},
    "easy_apply": {"-1"},
}

CITY_STATE = re.compile(r"^[^,]+, [A-Z]{2}$")


def snake_case(name):
    return re.sub(r"_+", "_", re.sub(r"[^0-9a-z]", "_", name.strip().lower())).strip("_")


def load_postings(csv_path=CSV_PATH):
    frame = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    frame.columns = [snake_case(column) for column in frame.columns]
    frame.insert(0, "row_id", range(1, len(frame) + 1))
    frame["company_name_clean"] = frame["company_name"].str.split("\n").str[0].str.strip()
    frame["description_key"] = (
        frame["job_description"].str.lower()
        .str.replace(r"[\r\n\t]", " ", regex=True)
        .str.replace(r" {2,}", " ", regex=True)
        .str.strip()
    )
    salary = frame["salary_estimate"]
    frame["pay_period"] = None
    frame.loc[salary != "-1", "pay_period"] = "annual"
    frame.loc[salary.str.contains("Per Hour", regex=False), "pay_period"] = "hourly"
    numbers = salary.str.extract(r"^\$(\d+)K?-\$(\d+)")
    frame["salary_low"] = pd.to_numeric(numbers[0])
    frame["salary_high"] = pd.to_numeric(numbers[1])
    frame["rating_value"] = pd.to_numeric(frame["rating"]).where(lambda value: value != -1)
    frame["founded_year"] = pd.to_numeric(frame["founded"]).where(lambda value: value != -1)
    return frame


def duplicate_postings(frame):
    key = ["job_title_key", "company_name_clean", "location", "description_key"]
    keyed = frame.assign(job_title_key=frame["job_title"].str.strip().str.lower())
    return set(keyed.loc[keyed.duplicated(subset=key, keep="first"), "row_id"])


def exact_duplicates_on_raw_fields(frame):
    key = ["job_title", "company_name", "location", "job_description"]
    return set(frame.loc[frame.duplicated(subset=key, keep="first"), "row_id"])


def hidden_missing_counts(frame):
    counts = {}
    for column, markers in MISSING_MARKERS.items():
        values = frame[column]
        missing = values.isin(markers) | (values.str.strip() == "")
        if column == "revenue":
            missing |= values.str.startswith("Unknown")
        if missing.sum():
            counts[column] = int(missing.sum())
    return counts


def salary_format_issues(frame):
    unparsed = frame["salary_low"].isna() | frame["salary_high"].isna()
    flagged = (
        (frame["salary_estimate"] == "-1")
        | (frame["pay_period"] == "hourly")
        | unparsed
        | (frame["salary_low"] == 0)
        | (frame["salary_high"] == 0)
        | (frame["salary_low"] > frame["salary_high"])
    )
    return set(frame.loc[flagged, "row_id"])


def company_name_issues(frame):
    flagged = (frame["company_name"].str.strip() == "") | frame["company_name"].str.contains("\n", regex=False)
    return set(frame.loc[flagged, "row_id"])


def location_format_issues(frame):
    flagged = ~frame["location"].str.match(CITY_STATE)
    return set(frame.loc[flagged, "row_id"])


def out_of_range_values(frame):
    rating = frame["rating_value"]
    annual = frame["pay_period"] == "annual"
    flagged = (
        rating.notna() & ((rating < 1) | (rating > 5))
        | (frame["founded_year"] > 2020)
        | ~frame["easy_apply"].isin(["True", "-1"])
        | annual & ((frame["salary_low"] < 10) | (frame["salary_high"] > 500))
    )
    return set(frame.loc[flagged, "row_id"])


def repeated_salary_blocks(frame, min_rows=10, min_companies=8):
    ordered = frame.sort_values("row_id")
    block = (ordered["salary_estimate"] != ordered["salary_estimate"].shift()).cumsum()
    summary = (
        ordered.assign(block=block)
        .loc[lambda data: data["salary_estimate"] != "-1"]
        .groupby("block")
        .agg(
            first_row_id=("row_id", "min"),
            last_row_id=("row_id", "max"),
            consecutive_rows=("row_id", "size"),
            distinct_companies=("company_name_clean", "nunique"),
        )
    )
    flagged = summary[(summary["consecutive_rows"] >= min_rows) & (summary["distinct_companies"] >= min_companies)]
    return set(zip(flagged["first_row_id"], flagged["last_row_id"]))


def main():
    download()
    frame = load_postings()
    print(f"Rows loaded with pandas: {len(frame):,}")
    print(f"Duplicate postings (normalised key): {len(duplicate_postings(frame)):,}")
    print(f"Duplicate postings (raw fields only): {len(exact_duplicates_on_raw_fields(frame)):,}")
    print(f"Salary format issues: {len(salary_format_issues(frame)):,}")
    print(f"Company name issues: {len(company_name_issues(frame)):,}")
    print(f"Rows with bad location format: {len(location_format_issues(frame)):,}")
    print(f"Out-of-range values: {len(out_of_range_values(frame)):,}")
    print(f"Repeated salary blocks: {len(repeated_salary_blocks(frame)):,}")
    print("Hidden missing values per column:")
    for column, count in sorted(hidden_missing_counts(frame).items(), key=lambda item: -item[1]):
        print(f"  {column:<20} {count:>6,}")


if __name__ == "__main__":
    main()
