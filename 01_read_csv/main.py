import csv
from io import StringIO

import pandas as pd
import polars as pl
import pyarrow as pa
import pyarrow.csv as pa_csv
import pyarrow.dataset as pa_ds


_csv_data = """
Index,First Name,Middle Name,Last Name
1,Mr. Al\, B.,grüBen,Johnson
2,"Mr. Al\, B.",grüBen,Johnson
3,\"Mr. Al\, B.\",grüBen,Johnson
4,Mr. Al\, B.,grüBen,Johnson
""".strip()

_csv_string = StringIO(_csv_data)

_file_path = "01_read_csv/data.csv"

_headers = ["Index", "First Name", "Middle Name", "Last Name"]


def main():
    read_csv_std(_file_path)
    validate_csv_std(_file_path)
    read_csv_pandas(_csv_string)
    read_csv_pandas_with_provided_headers(_file_path)
    read_csv_pandas_with_pyarrow_engine(_file_path)
    read_csv_pandas_starting_at_first_valid_data_row(_file_path)
    read_csv_pyarrow(_file_path)
    read_csv_pyarrow_stream(_file_path)
    read_csv_pyarrow_batch(_file_path)
    # read_csv_polars(file)
    # validate_csv_pandas_by_casting(file)


def print_block(text: str) -> None:
    print(f"\n====== {text} ======")


def read_csv_std(file_path: str) -> None:
    print_block("Read STD/CSV")
    with open(file_path, newline="") as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            print(f"i={i}, len={len(row)} -> {row}")


def validate_csv_std(file_path: str) -> None:
    print_block("Validate STD/CSV")
    with open(file_path, newline="") as file:
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


def read_csv_pandas(csv) -> None:
    print_block("Read PANDAS default")
    df = pd.read_csv(
        csv,
        on_bad_lines="skip",  # does nothing whether 'warn' or 'skip' - silently moves the columns around - see logs
    )
    print_df(df)


def read_csv_pandas_with_provided_headers(csv) -> None:
    print_block("Read PANDAS with provided headers")
    df = pd.read_csv(
        csv,
        names=_headers,  # works but have to know headers or read csv upfront, and the column ends up as a row in the df
        on_bad_lines="skip",
    )
    print_df(df)


def read_csv_pandas_with_pyarrow_engine(csv) -> None:
    print_block("Read PANDAS with pyarrow engine")
    df = pd.read_csv(
        csv,
        engine="pyarrow",  # this gives the desired result, but not fully sure of the implications of switching
        on_bad_lines=_skip_invalid_rows,
    )
    print_df(df)


def read_csv_pandas_starting_at_first_valid_data_row(file_path: str) -> None:
    print_block("Read PANDAS starting at first valid data row")

    skip_rows = []
    with open(file_path, newline="") as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            if i == 0 and row == _headers:
                continue
            elif len(row) != len(_headers):
                skip_rows.append(i)
            else:
                break

    config = {
        "header": 0,
        "names": _headers,
        "skiprows": skip_rows,
        "on_bad_lines": "skip",
    }
    print("config:", config)

    df = pd.read_csv(file_path, **config)
    print_df(df)


def read_csv_pyarrow(file_path: str) -> None:
    print_block("Read PYARROW default")
    columns_in_csv = True
    read_optsions = pa_csv.ReadOptions(
        column_names=_headers if not columns_in_csv else None,
        skip_rows=0 if columns_in_csv else None,
    )
    parse_options = pa_csv.ParseOptions(invalid_row_handler=_skip_invalid_rows)
    convert_options = pa_csv.ConvertOptions()
    table = pa_csv.read_csv(
        file_path,
        read_options=read_optsions,
        parse_options=parse_options,
        convert_options=convert_options,
    )
    df = table.to_pandas()
    print_df(df)


def read_csv_pyarrow_stream(file_path: str) -> None:
    print_block("Read PYARROW stream")
    columns_in_csv = True
    read_optsions = pa_csv.ReadOptions(
        column_names=_headers if not columns_in_csv else None,
        skip_rows=0 if columns_in_csv else None,
    )
    parse_options = pa_csv.ParseOptions(invalid_row_handler=_skip_invalid_rows)
    convert_options = pa_csv.ConvertOptions()
    stream = pa_csv.open_csv(
        file_path,
        read_options=read_optsions,
        parse_options=parse_options,
        convert_options=convert_options,
    )
    df = stream.read_pandas()
    print_df(df)


def read_csv_pyarrow_batch(file_path: str) -> None:
    print_block("Read PYARROW batch")
    chunksize = 2
    columns_in_csv = True
    read_optsions = pa_csv.ReadOptions(
        column_names=_headers if not columns_in_csv else None,
        skip_rows=0 if columns_in_csv else None,
    )
    parse_options = pa_csv.ParseOptions(invalid_row_handler=_skip_invalid_rows)
    convert_options = pa_csv.ConvertOptions()
    csv_format = pa_ds.CsvFileFormat(
        read_options=read_optsions,
        parse_options=parse_options,
        convert_options=convert_options,
    )
    dataset = pa_ds.dataset(file_path, format=csv_format)
    scanner = pa_ds.Scanner.from_dataset(dataset, batch_size=chunksize)
    for i, batch in enumerate(scanner.to_batches()):
        df = pl.from_arrow(batch)
        print(f"Batch [{i}]:", df)


def _skip_invalid_rows(invalid_row: pa_csv.InvalidRow) -> str:
    return "skip"


def read_csv_polars(csv) -> None:
    print_block("Read POLARS default")
    df = pl.read_csv(
        csv,
        columns=["Index", "First Name", "Middle Name", "Last Name"],
        use_pyarrow=True,
        infer_schema=False,
        ignore_errors=True,
    )
    print_df(df)


def validate_csv_pandas_by_casting(csv) -> None:
    print_block("Validate PANDAS by type casting")
    pd.read_csv(
        csv,
        converters={"Index": validated_int},
    )


def validated_int(x: str) -> int:
    return int(x)  # pandas will raise a ValueError if this isn't an int


def print_df(df):
    # _print_df_custom(df)
    _print_df_std(df)


def _print_df_custom(df) -> None:
    headers = df.columns.to_list()
    print(f"i=0, len={len(headers)} -> {headers}")
    for i, row in df.iterrows():
        values = row.tolist()
        print(f"i={i}, len={len(values)} -> {values}")


def _print_df_std(df) -> None:
    print(df)


if __name__ == "__main__":
    main()
