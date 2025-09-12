import csv
import pandas as pd
import polars as pl
import pyarrow as pa
import pyarrow.csv as pacsv


def main():
    file = "data.csv"

    print_block("Read STD/CSV")
    read_csv_std(file)

    print_block("Validate STD/CSV")
    validate_csv_std(file)

    print_block("Read PANDAS default")
    read_csv_pandas(file)

    print_block("Read PANDAS with provided headers")
    read_csv_pandas_with_provided_headers(file)

    print_block("Read PANDAS with pyarrow engine")
    read_csv_pandas_with_pyarrow_engine(file)

    print_block("Read PYARROW default")
    read_csv_pyarrow(file)

    print_block("Read PYARROW incremental")
    read_csv_pyarrow_incremental(file)

    print_block("Read PANDAS starting at first valid data row")
    read_csv_pandas_starting_at_first_valid_data_row(file)

    print_block("Read POLARS default")
    read_csv_polars(file)

    print_block("Validate PANDAS by type casting")
    validate_csv_pandas_by_casting(file)


def print_block(text):
    print(f"\n====== {text} ======")


def read_csv_std(path):
    with open(path, newline="") as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            print(f"i={i}, len={len(row)} -> {row}")


def validate_csv_std(path):
    with open(path, newline="") as file:
        reader = csv.reader(file)
        headers = next(reader)
        num_columns = len(headers)
        for i, row in enumerate(reader, start=1):
            if len(row) != num_columns:
                print(
                    f"i={i} - ❌ - expected {num_columns} fields, saw {len(row)} -> {row}"
                )
            else:
                print(f"i={i} - ✅ - expected {num_columns} fields, saw {len(row)}")


def read_csv_pandas(path):
    df = pd.read_csv(
        path,
        on_bad_lines="error",  # does nothing whether 'warn' or 'skip' - silently moves the columns around - see logs
    )
    print_df(df)


def read_csv_pandas_with_provided_headers(path):
    df = pd.read_csv(
        path,
        names=_headers,  # works but have to know headers or read csv upfront, and the column ends up as a row in the df
        on_bad_lines="skip",
    )
    print_df(df)


def read_csv_pandas_with_pyarrow_engine(path):
    df = pd.read_csv(
        path,
        engine="pyarrow",  # this gives the desired result, but not fully sure of the implications of switching
        on_bad_lines="skip",
    )
    print_df(df)


def read_csv_pandas_starting_at_first_valid_data_row(path):
     with open(path, newline="") as file:
        reader = csv.reader(file)

        idx_header: int = -1
        idx_first_valid_data_row: int = -1

        for i, row in enumerate(reader):
            if i == 0 and _is_header(row):
                idx_header = 0
                continue
            if _is_valid_length(row):
                idx_first_valid_data_row = i
                break
        
        if idx_first_valid_data_row == -1:
            raise Exception('No valid data rows found')
        
        skip_rows = [i for i in range(idx_header, idx_first_valid_data_row)]
        print("skip_rows:", skip_rows)

        df = pd.read_csv(
            path,
            names=_headers,
            skiprows=skip_rows,
            on_bad_lines="skip",
        )
        print_df(df)


def read_csv_pyarrow(path):
    table = pacsv.read_csv(
        path,
        parse_options=pacsv.ParseOptions(
            invalid_row_handler=skip_handler
        ),
        read_options=pacsv.ReadOptions(
            block_size=50,
        ),
    )
    df = table.to_pandas()
    print_df(df)


def read_csv_pyarrow_incremental(path):
    stream = pacsv.open_csv(
        path,
        parse_options=pacsv.ParseOptions(
            invalid_row_handler=skip_handler
        ),
        read_options=pacsv.ReadOptions(
            block_size=50,
        ),
    )
    df = stream.read_pandas()
    print_df(df)


def skip_handler(invalid_row):
    return "skip"


def read_csv_polars(path):
    df = pl.read_csv(
        path,
        columns=["Index", "First Name", "Middle Name", "Last Name"],
        use_pyarrow=True,
        infer_schema=False,
        ignore_errors=True,
    )
    print_df(df)


def validate_csv_pandas_by_casting(path):
    pd.read_csv(
        path,
        converters={ "Index": validated_int },
    )


def validated_int(x: str) -> int:
    return int(x)  # pandas will raise a ValueError if this isn't an int


def print_df(df):
    #_print_df_custom(df)
    _print_df_std(df)


def _print_df_custom(df):
    headers = df.columns.to_list()
    print(f"i=0, len={len(headers)} -> {headers}")
    for i, row in df.iterrows():
        values = row.tolist()
        print(f"i={i}, len={len(values)} -> {values}")


def _print_df_std(df):
    print(df)


_headers = ["Index", "First Name", "Middle Name", "Last Name"]


def _is_header(row: list[str], headers: list[str] = _headers) -> bool:
    return _compare_strings(row, headers)


def _is_valid_length(row: list[str], length: int = len(_headers)) -> bool:
    return len(row) == length


def _compare_strings(a: list[str], b: list[str]) -> bool:
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if a[i] != b[i]:
            return False
    return True


main()
