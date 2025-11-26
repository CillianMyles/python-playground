#!/usr/bin/env python3
import sys
from pathlib import Path
import argparse
from typing import List, Sequence

import polars as pl
from polars.testing import assert_frame_equal


def load_csv(path: str | Path) -> pl.DataFrame:
    return pl.read_csv(path)


def normalize_df(
    df: pl.DataFrame,
    ignore_cols: Sequence[str] | None = None,
    sort_rows: bool = True,
) -> pl.DataFrame:
    """
    - Lowercase all column names
    - Drop ignored columns (case-insensitive)
    - Sort columns
    - Optionally sort rows by all columns (so row order doesn't matter)
    """
    # lowercase columns
    lower_map = {c: c.lower() for c in df.columns}
    df = df.rename(lower_map)

    # drop ignored columns (case-insensitive)
    ignore_set = {c.lower() for c in (ignore_cols or [])}
    if ignore_set:
        cols_to_keep = [c for c in df.columns if c.lower() not in ignore_set]
        df = df.select(cols_to_keep)

    # sort columns by name
    df = df.select(sorted(df.columns))

    # if you want row-order-insensitive comparison, sort by all columns:
    if sort_rows and df.columns:
        df = df.sort(df.columns)

    return df


def quick_assert_equal(name_a: str, df_a: pl.DataFrame,
                       name_b: str, df_b: pl.DataFrame) -> bool:
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

        # Avoid numpy to dodge np.int64 indexing issues
        mask_list = mask.to_list()
        for row_idx, is_diff in enumerate(mask_list):
            if not is_diff:
                continue
            if len(diffs) >= max_rows:
                break

            # Polars likes plain Python ints; row_idx is already int
            val_a = a_series[row_idx]
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

    # Basic shape info
    print(f"Shape A ({name_a}): {df_a.shape}")
    print(f"Shape B ({name_b}): {df_b.shape}\n")

    # Schema / columns
    summarize_schema_diff(df_a, df_b)

    # If shape & columns identical, show cell-level diffs
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
    csv_has_header: bool = True,
) -> None:
    paths = [csv1, csv2, csv3]
    names = ["A", "B", "C"]

    print("Loading CSVs...")
    dfs = [
        normalize_df(load_csv(p), ignore_cols=ignore_cols)
        for p in paths
    ]

    # v1: simple assert frame equal on normalised data
    print("==== Quick equality checks (assert_frame_equal) ====")
    equal_ab = quick_assert_equal("A", dfs[0], "B", dfs[1])
    equal_ac = quick_assert_equal("A", dfs[0], "C", dfs[2])
    equal_bc = quick_assert_equal("B", dfs[1], "C", dfs[2])

    # If all equal, we’re done.
    if equal_ab and equal_ac and equal_bc:
        print("\nAll three DataFrames are equal (after normalisation).")
        return

    # Otherwise, detailed diffs
    print("\n==== Detailed differences ====\n")
    if not equal_ab:
        diff_pair("A", dfs[0], "B", dfs[1], csv_has_header=csv_has_header)
    if not equal_ac:
        diff_pair("A", dfs[0], "C", dfs[2], csv_has_header=csv_has_header)
    if not equal_bc:
        diff_pair("B", dfs[1], "C", dfs[2], csv_has_header=csv_has_header)


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
        "--no-header",
        action="store_true",
        help="Set this if the CSVs do NOT have a header row.",
    )
    return parser.parse_args(argv[1:])


def main(argv: List[str]) -> None:
    args = parse_args(argv)
    compare_three(
        args.csv1,
        args.csv2,
        args.csv3,
        ignore_cols=args.ignore_cols,
        csv_has_header=not args.no_header,
    )


if __name__ == "__main__":
    main(sys.argv)
