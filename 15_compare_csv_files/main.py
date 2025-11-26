#!/usr/bin/env python3
import sys
from pathlib import Path
import argparse
from typing import List, Sequence, Dict

import polars as pl
from polars.testing import assert_frame_equal


def load_csv(path: str | Path) -> pl.DataFrame:
    return pl.read_csv(path)


def apply_renames_case_insensitive(
    df: pl.DataFrame,
    rename_map: Dict[str, str],
) -> pl.DataFrame:
    """
    Apply a rename map in a case-insensitive way.

    rename_map keys and values are assumed to be *logical* names after
    lowercasing. For example, if rename_map is:
        {"street_address": "address"}
    and df has column "Street_Address", it will be:
        "Street_Address" -> "address"
    """
    if not rename_map:
        return df

    # Build a mapping from lowercased current column name -> actual column name
    lower_to_actual = {c.lower(): c for c in df.columns}

    # Build a Polars rename dict using actual column names
    actual_rename = {}
    for src_lower, dst_lower in rename_map.items():
        if src_lower in lower_to_actual:
            actual_src = lower_to_actual[src_lower]
            actual_rename[actual_src] = dst_lower

    if actual_rename:
        df = df.rename(actual_rename)

    return df


def normalize_df(
    df: pl.DataFrame,
    ignore_cols: Sequence[str] | None = None,
    rename_map: Dict[str, str] | None = None,
    sort_rows: bool = True,
) -> pl.DataFrame:
    """
    - Lowercase all column names
    - Apply column renames (case-insensitive)
    - Drop ignored columns (case-insensitive)
    - Sort columns by name
    - Optionally sort rows by all columns
    """
    # Step 1: lowercase columns
    lower_map = {c: c.lower() for c in df.columns}
    df = df.rename(lower_map)

    # Step 2: apply logical renames (mapping already expected to be lowercase)
    df = apply_renames_case_insensitive(df, rename_map or {})

    # Step 3: drop ignored columns (case-insensitive)
    ignore_set = {c.lower() for c in (ignore_cols or [])}
    if ignore_set:
        cols_to_keep = [c for c in df.columns if c.lower() not in ignore_set]
        df = df.select(cols_to_keep)

    # Step 4: sort columns by name
    df = df.select(sorted(df.columns))

    # Step 5: optionally sort rows
    if sort_rows and df.columns:
        df = df.sort(df.columns)

    return df


def quick_assert_equal(
    name_a: str, df_a: pl.DataFrame, name_b: str, df_b: pl.DataFrame
) -> bool:
    """
    Use polars' builtin assert_frame_equal; returns True if equal, False otherwise.
    """
    try:
        assert_frame_equal(df_a, df_b, check_row_order=True, check_column_order=True)
        print(f"[OK] {name_a} == {name_b}")
        return True
    except AssertionError as e:
        print(f"[FAIL] {name_a} != {name_b}")
        print(f"Reason from assert_frame_equal:\n{e}\n")
        return False


def summarize_schema_diff(df_a: pl.DataFrame, df_b: pl.DataFrame) -> None:
    print("Schema comparison:")
    cols_a = set(df_a.columns)
    cols_b = set(df_b.columns)

    only_a = cols_a - cols_b
    only_b = cols_b - cols_a
    both = cols_a & cols_b

    if only_a:
        print("  Columns only in A:", sorted(only_a))
    if only_b:
        print("  Columns only in B:", sorted(only_b))
    if both:
        type_diffs = []
        for c in sorted(both):
            ta = df_a.schema[c]
            tb = df_b.schema[c]
            if ta != tb:
                type_diffs.append((c, ta, tb))
        if type_diffs:
            print("  Columns with differing dtypes:")
            for c, ta, tb in type_diffs:
                print(f"    {c}: A={ta}, B={tb}")
        else:
            print("  Shared columns have matching dtypes.")
    print()


def cell_diff_by_position(
    df_a: pl.DataFrame,
    df_b: pl.DataFrame,
    max_rows: int = 20,
    csv_has_header: bool = True,
) -> None:
    """
    Compare cell values by *position* (row index + column name).
    Assumes same shape and same columns.
    Prints up to max_rows differences.

    Also prints an approximate CSV line number:
    - If csv_has_header=True, then csv_line = row_idx + 2
      (1-based including header row)
    """
    if df_a.height != df_b.height or df_a.width != df_b.width:
        print("Cannot do positional cell diff: shapes differ.")
        print(f"  A shape: {df_a.shape}, B shape: {df_b.shape}\n")
        return

    cols = df_a.columns
    diffs = []

    for col in cols:
        a_series = df_a[col]
        b_series = df_b[col]

        # boolean mask where values differ (including null vs non-null)
        mask = (a_series != b_series) | (a_series.is_null() ^ b_series.is_null())

        mask_list = mask.to_list()
        for row_idx, is_diff in enumerate(mask_list):
            if not is_diff:
                continue
            if len(diffs) >= max_rows:
                break

            val_a = a_series[row_idx]  # row_idx is plain int
            val_b = b_series[row_idx]

            csv_line = row_idx + (2 if csv_has_header else 1)

            diffs.append(
                {
                    "row_idx": row_idx,
                    "csv_line": csv_line,
                    "column": col,
                    "A": val_a,
                    "B": val_b,
                }
            )
        if len(diffs) >= max_rows:
            break

    if not diffs:
        print("No cell-level differences found (same shape & columns).")
        print()
        return

    print(f"First {len(diffs)} cell-level differences (by position):")
    for d in diffs:
        print(
            f"  row_idx={d['row_idx']}, csv_line={d['csv_line']}, "
            f"col='{d['column']}': A={d['A']!r}, B={d['B']!r}"
        )
    if len(diffs) >= max_rows:
        print(f"  ...stopped after {max_rows} differences.\n")
    else:
        print()


def diff_pair(
    name_a: str,
    df_a: pl.DataFrame,
    name_b: str,
    df_b: pl.DataFrame,
    csv_has_header: bool = True,
) -> None:
    print(f"===== Detailed diff: {name_a} vs {name_b} =====")

    print(f"Shape A ({name_a}): {df_a.shape}")
    print(f"Shape B ({name_b}): {df_b.shape}\n")

    summarize_schema_diff(df_a, df_b)

    same_cols = df_a.columns == df_b.columns
    if df_a.shape == df_b.shape and same_cols:
        cell_diff_by_position(df_a, df_b, csv_has_header=csv_has_header)
    else:
        print("Skip cell-level diff since shape or column sets differ.\n")


def compare_three(
    csv1: str,
    csv2: str,
    csv3: str,
    ignore_cols: Sequence[str] | None = None,
    rename_map: Dict[str, str] | None = None,
    csv_has_header: bool = True,
    sort_rows: bool = True,
) -> None:
    paths = [csv1, csv2, csv3]

    print("Loading CSVs...")
    dfs = [
        normalize_df(
            load_csv(p),
            ignore_cols=ignore_cols,
            rename_map=rename_map,
            sort_rows=sort_rows,
        )
        for p in paths
    ]

    print("==== Quick equality checks (assert_frame_equal) ====")
    equal_ab = quick_assert_equal("A", dfs[0], "B", dfs[1])
    equal_ac = quick_assert_equal("A", dfs[0], "C", dfs[2])
    equal_bc = quick_assert_equal("B", dfs[1], "C", dfs[2])

    if equal_ab and equal_ac and equal_bc:
        print("\nAll three DataFrames are equal (after normalisation).")
        return

    print("\n==== Detailed differences ====\n")
    if not equal_ab:
        diff_pair("A", dfs[0], "B", dfs[1], csv_has_header=csv_has_header)
    if not equal_ac:
        diff_pair("A", dfs[0], "C", dfs[2], csv_has_header=csv_has_header)
    if not equal_bc:
        diff_pair("B", dfs[1], "C", dfs[2], csv_has_header=csv_has_header)


def parse_rename_args(rename_args: Sequence[str]) -> Dict[str, str]:
    """
    Parse --rename-col 'old=new' arguments into a dict {old_lower: new_lower}.
    """
    result: Dict[str, str] = {}
    for arg in rename_args:
        if "=" not in arg:
            raise ValueError(f"Invalid --rename-col value (expected old=new): {arg}")
        old, new = arg.split("=", 1)
        result[old.strip().lower()] = new.strip().lower()
    return result


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare three CSV files using Polars."
    )
    parser.add_argument("csv1", help="Path to CSV file A")
    parser.add_argument("csv2", help="Path to CSV file B")
    parser.add_argument("csv3", help="Path to CSV file C")

    parser.add_argument(
        "--ignore-cols",
        nargs="+",
        default=[],
        help=(
            "Column names to ignore when comparing. "
            "Case-insensitive and applied after lowercasing column names."
        ),
    )

    parser.add_argument(
        "--rename-col",
        action="append",
        default=[],
        help=(
            "Rename a column before comparison, in the form old=new. "
            "Can be passed multiple times. Case-insensitive on both sides."
        ),
    )

    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Set this if the CSVs do NOT have a header row.",
    )

    parser.add_argument(
        "--no-sort-rows",
        action="store_true",
        help="Disable row sorting during normalisation (keep original order).",
    )

    return parser.parse_args(argv[1:])


def main(argv: List[str]) -> None:
    args = parse_args(argv)
    rename_map = parse_rename_args(args.rename_col)

    compare_three(
        args.csv1,
        args.csv2,
        args.csv3,
        ignore_cols=args.ignore_cols,
        rename_map=rename_map,
        csv_has_header=not args.no_header,
        sort_rows=not args.no_sort_rows,
    )


if __name__ == "__main__":
    main(sys.argv)
