import pandas as pd

# import numpy as np
import re
from typing import Any
from src.utils.constants import state, cateogry


df1 = pd.read_csv("data/Prospects_5000_12052025_040201.csv", low_memory=False)
df2 = pd.read_csv("data/Prospects_trimmed_for_reasoning.csv", low_memory=False)


def clean_number(val) -> Any:
    if pd.isnull(val) or val == "-":
        return None
    val = str(val).replace(",", "").replace("$", "").strip()
    mult = 1
    val = val.replace("K", "k").replace("M", "m")
    if "k" in val:
        mult = 1000
        val = val.replace("k", "")
    if "m" in val:
        mult = 1_000_000
        val = val.replace("m", "")
    try:
        return float(re.findall(r"[\d.]+", val)[0]) * mult
    except Exception:
        return None


def number_in_filter(value, flt):
    value_num = clean_number(value)
    if value_num is None:
        return False
    low, high = flt
    if low is not None and value_num < low:
        return False
    if high is not None and value_num > high:
        return False
    return True


def split_and_strip(s) -> Any:
    if pd.isnull(s) or s == "-":
        return []
    return [x.strip().lower() for x in str(s).split(",")]


def try_parse_range(valstr) -> Any:
    # Handles "$5K - $50K" or "$50K - $100K" etc.
    # Returns (low, high), both numbers or None
    valstr = valstr.replace("$", "").replace(",", "").upper()
    parts = re.split(r"\s*-\s*", valstr)
    if len(parts) == 2:
        low = clean_number(parts[0])
        high = clean_number(parts[1])
        return (low, high)
    # For ">$5K" or "$5K+" style
    if "+" in valstr:
        low = clean_number(valstr.replace("+", ""))
        return (low, None)
    if "<" in valstr:  # "<$1K"
        high = clean_number(valstr.replace("<", ""))
        return (None, high)
    # If only a single value, treat as [val, val]
    if clean_number(valstr) is not None:
        n = clean_number(valstr)
        return (n, n)
    return (None, None)


def number_in_any_filter(value, filtvals) -> Any:
    # filtvals can be list of str/ranges ("$5K - $50K", "$50K - $100K", ...)
    value_num = clean_number(value)
    if value_num is None:
        return False
    for bucket in filtvals:
        # If bucket is a string range, convert to [low, high]
        if isinstance(bucket, str):
            low, high = try_parse_range(bucket)
        elif isinstance(bucket, (list, tuple)) and len(bucket) == 2:
            low, high = bucket
        else:
            continue
        if low is not None and value_num < low:
            continue
        if high is not None and value_num > high:
            continue
        return True
    return False


def match_filter(val, filval):
    # Yes/No
    if isinstance(filval, list) and all(v.lower() in ["yes", "no"] for v in filval):
        val = str(val).strip().lower()
        return val in [v.lower() for v in filval]
    # Numerical as bucket strings or raw ranges
    if isinstance(filval, list) and any(
        ("$" in str(f) or "-" in str(f)) for f in filval
    ):
        # At least one is a range-bucket string like "$5K - $50K"
        return number_in_any_filter(val, filval)
    # Direct range e.g., [5000, None]
    if (
        isinstance(filval, list)
        and len(filval) == 2
        and (
            isinstance(filval[0], (int, float, type(None)))
            or isinstance(filval[1], (int, float, type(None)))
        )
    ):
        return number_in_any_filter(val, [filval])
    # String list matching
    if isinstance(filval, list):
        val_list = split_and_strip(val)
        return any(f.lower() in val_list for f in filval if isinstance(f, str))
    # Single string (rare, fallback)
    if isinstance(filval, str):
        return str(val).strip().lower() == filval.lower()
    return False


# --- Main filtering function ---


def extract_rows_and_match_details(filter_result) -> Any:
    full_de = df1[(df1["Primary Category"] == cateogry) & (df1["State"] == state)]
    partialdf = full_de[df2.columns]
    df = partialdf
    results = []
    if not filter_result:
        return results
    for idx, row in df.iterrows():
        matched_filters = []
        unmatched_filters = []
        for filt in filter_result:
            col = filt["Filter_Name"]
            values = filt["Filter_value"]
            if col not in df.columns:
                unmatched_filters.append(col)
                continue
            if match_filter(row[col], values):
                matched_filters.append(col)
            else:
                unmatched_filters.append(col)
        # OR: include row if matched_filters is not empty
        if matched_filters:
            percent = round(100 * len(matched_filters) / len(filter_result), 1)
            results.append(
                {
                    "Company Name": row.get("Company Name", ""),
                    "Matched Filters": matched_filters,
                    "Unmatched Filters": unmatched_filters,
                    "Match %": percent,
                }
            )
    # --- Sort in-place in descending order of "Match %"
    results_sorted = sorted(results, key=lambda x: -x["Match %"])
    return results_sorted
