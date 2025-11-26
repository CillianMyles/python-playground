#!/usr/bin/env python3
import sys
from pathlib import Path
import polars as pl
from polars.testing import assert_frame_equal


def load_csv(path: str | Path) -> pl.DataFrame:
    return pl.read_csv(path)


def normalize_df(df: pl.DataFrame) -> pl.DataFrame:
    """
    Normalization step so that small differences don't blow up the comparison.
    Adjust as needed:
    - Sort columns
    - Sort rows (if order is not important)
    """
    # sort columns by name
    df = df.select(sorted(df.columns))

    # if you want row-order-insensitive comparison, sort by all columns:
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
    print()


def cell_diff_by_position(
    df_a: pl.DataFrame, df_b: pl.DataFrame, max_rows: int = 20
) -> None:
    """
    Compare cell values by *position* (row index + column name).
    Assumes same shape and same columns.
    Prints up to max_rows differences.
    """
    if df_a.height != df_b.height or df_a.width != df_b.width:
        print("Cannot do positional cell diff: shapes differ.")
        print(f"  A shape: {df_a.shape}, B shape: {df_b.shape}\n")
        return

    cols = df_a.columns
    # collect differences in a list of rows
    diffs = []

    # Compare column by column using vectorised ops for speed
    for col in cols:
        a_series = df_a[col]
        b_series = df_b[col]
        mask = a_series.ne(b_series) | (a_series.is_null() ^ b_series.is_null())
        if mask.any():
            idxs = mask.to_numpy().nonzero()[0]
            for i in idxs:
                if len(diffs) >= max_rows:
                    break
                diffs.append(
                    {
                        "row_idx": i,
                        "column": col,
                        "A": a_series[i],
                        "B": b_series[i],
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
        print(f"  row={d['row_idx']}, col='{d['column']}': A={d['A']!r}, B={d['B']!r}")
    if len(diffs) >= max_rows:
        print(f"  ...stopped after {max_rows} differences.\n")
    else:
        print()


def diff_pair(name_a: str, df_a: pl.DataFrame, name_b: str, df_b: pl.DataFrame) -> None:
    print(f"===== Detailed diff: {name_a} vs {name_b} =====")

    # Basic shape info
    print(f"Shape A ({name_a}): {df_a.shape}")
    print(f"Shape B ({name_b}): {df_b.shape}\n")

    # Schema / columns
    summarize_schema_diff(df_a, df_b)

    # If shape & columns identical, show cell-level diffs
    same_cols = df_a.columns == df_b.columns
    if df_a.shape == df_b.shape and same_cols:
        cell_diff_by_position(df_a, df_b)
    else:
        print("Skip cell-level diff since shape or column sets differ.\n")


def compare_three(csv1: str, csv2: str, csv3: str) -> None:
    paths = [csv1, csv2, csv3]
    names = ["A", "B", "C"]

    print("Loading CSVs...")
    dfs = [normalize_df(load_csv(p)) for p in paths]

    # v1: simple assert frame equal
    print("==== Quick equality checks (assert_frame_equal) ====")
    equal_ab = quick_assert_equal("A", dfs[0], "B", dfs[1])
    equal_ac = quick_assert_equal("A", dfs[0], "C", dfs[2])
    equal_bc = quick_assert_equal("B", dfs[1], "C", dfs[2])

    # If all equal, we’re done.
    if equal_ab and equal_ac and equal_bc:
        print("\nAll three DataFrames are equal.")
        return

    # Otherwise, detailed diffs
    print("\n==== Detailed differences ====\n")
    if not equal_ab:
        diff_pair("A", dfs[0], "B", dfs[1])
    if not equal_ac:
        diff_pair("A", dfs[0], "C", dfs[2])
    if not equal_bc:
        diff_pair("B", dfs[1], "C", dfs[2])


def main(argv: list[str]) -> None:
    if len(argv) != 4:
        print(f"Usage: {argv[0]} file_A.csv file_B.csv file_C.csv")
        raise SystemExit(1)
    _, csv1, csv2, csv3 = argv
    compare_three(csv1, csv2, csv3)


if __name__ == "__main__":
    main(sys.argv)
