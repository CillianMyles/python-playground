import csv
import pandas as pd
import polars as pl
import pyarrow as pa
import pyarrow.csv as pacsv


def main():
    file = "data.csv"
    read_csv_std(file)
    validate_csv_std(file)
    read_csv_pandas(file)
    read_csv_pandas_with_provided_headers(file)
    read_csv_pandas_with_pyarrow_engine(file)
    read_csv_pandas_starting_at_first_valid_data_row(file)
    read_csv_pyarrow(file)
    read_csv_pyarrow_incremental(file)
    #read_csv_polars(file)
    #validate_csv_pandas_by_casting(file)


def print_block(text: str) -> None:
    print(f"\n====== {text} ======")


def read_csv_std(path: str) -> None:
    print_block("Read STD/CSV")
    with open(path, newline="") as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            print(f"i={i}, len={len(row)} -> {row}")


def validate_csv_std(path: str) -> None:
    print_block("Validate STD/CSV")
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


def read_csv_pandas(path: str) -> None:
    print_block("Read PANDAS default")
    df = pd.read_csv(
        path,
        on_bad_lines="skip",  # does nothing whether 'warn' or 'skip' - silently moves the columns around - see logs
    )
    print_df(df)


def read_csv_pandas_with_provided_headers(path: str) -> None:
    print_block("Read PANDAS with provided headers")
    df = pd.read_csv(
        path,
        names=_headers,  # works but have to know headers or read csv upfront, and the column ends up as a row in the df
        on_bad_lines="skip",
    )
    print_df(df)


def read_csv_pandas_with_pyarrow_engine(path: str) -> None:
    print_block("Read PANDAS with pyarrow engine")
    df = pd.read_csv(
        path,
        engine="pyarrow",  # this gives the desired result, but not fully sure of the implications of switching
        on_bad_lines="skip",
    )
    print_df(df)


def read_csv_pandas_starting_at_first_valid_data_row(path: str) -> None:
    print_block("Read PANDAS starting at first valid data row")

    header_row: int = -1
    first_valid_data_row: int = -1
    
    with open(path, newline="") as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            if i == 0 and _is_header(row):
                header_row = i
                continue
            if _is_valid_length(row):
                first_valid_data_row = i
                break
    
    if first_valid_data_row == -1:
        raise Exception('No valid data rows found')
    
    skip_rows = [i for i in range(header_row + 1, first_valid_data_row)]
    config = {
        "names": _headers,
        "header": header_row if header_row != -1 else None,
        "skiprows": skip_rows,
        "on_bad_lines": "skip",
    }
    print("config:", config)

    df = pd.read_csv(path, **config)
    print_df(df)


def read_csv_pyarrow(path: str) -> None:
    print_block("Read PYARROW default")
    table = pacsv.read_csv(
        path,
        parse_options=pacsv.ParseOptions(
            invalid_row_handler=skip_handler
        ),
        read_options=pacsv.ReadOptions(
            column_names=_headers,
        ),
    )
    df = table.to_pandas()
    print_df(df)


def read_csv_pyarrow_incremental(path: str) -> None:
    print_block("Read PYARROW incremental")
    stream = pacsv.open_csv(
        path,
        parse_options=pacsv.ParseOptions(
            invalid_row_handler=skip_handler
        ),
        read_options=pacsv.ReadOptions(
            column_names=_headers,
        ),
    )
    for i, chunk in enumerate(stream):
        df = chunk.to_pandas()
        print(f"Chunk [{i}]:", df)


def skip_handler(invalid_row) -> str:
    return "skip"


def read_csv_polars(path: str) -> None:
    print_block("Read POLARS default")
    df = pl.read_csv(
        path,
        columns=["Index", "First Name", "Middle Name", "Last Name"],
        use_pyarrow=True,
        infer_schema=False,
        ignore_errors=True,
    )
    print_df(df)


def validate_csv_pandas_by_casting(path: str) -> None:
    print_block("Validate PANDAS by type casting")
    pd.read_csv(
        path,
        converters={ "Index": validated_int },
    )


def validated_int(x: str) -> int:
    return int(x)  # pandas will raise a ValueError if this isn't an int


def print_df(df):
    #_print_df_custom(df)
    _print_df_std(df)


def _print_df_custom(df) -> None:
    headers = df.columns.to_list()
    print(f"i=0, len={len(headers)} -> {headers}")
    for i, row in df.iterrows():
        values = row.tolist()
        print(f"i={i}, len={len(values)} -> {values}")


def _print_df_std(df) -> None:
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
