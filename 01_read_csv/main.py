import csv
import pandas as pd
import polars as pl


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
    print_block("Read POLARS default")
    read_csv_polars(file)
    print_block("Validate PANDAS by type casting")
    validate_csv_pandas_by_casting(file)


def print_block(text):
    print(f"====== {text} ======")


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
    headers = df.columns.to_list()
    print(f"i=0, len={len(headers)} -> {headers}")
    for i, row in df.iterrows():
        values = row.tolist()
        print(f"i={i}, len={len(values)} -> {values}")


def read_csv_pandas_with_provided_headers(path):
     with open(path, newline="") as file:
        reader = csv.reader(file)
        headers = next(reader)
        print(f"i=0, len={len(headers)} -> {headers}")
        df = pd.read_csv(
            path,
            names=headers,  # works but we end have to read the csv upfront, and the column ends up as a row in the df
            on_bad_lines="skip",
        )
        for i, row in df.iterrows():
            values = row.tolist()
            print(f"i={i}, len={len(values)} -> {values}")


def read_csv_pandas_with_pyarrow_engine(path):
    df = pd.read_csv(
        path,
        engine="pyarrow",  # this gives the desired result, but not fully sure of the implications of switching
        on_bad_lines="skip",
    )
    headers = df.columns.to_list()
    print(f"i=0, len={len(headers)} -> {headers}")
    for i, row in df.iterrows():
        values = row.tolist()
        print(f"i={i}, len={len(values)} -> {values}")


def read_csv_polars(path):
    df = pl.read_csv(
        path,
        use_pyarrow=True,
        infer_schema=False,
        ignore_errors=True,
    )
    headers = df.columns.to_list()
    print(f"i=0, len={len(headers)} -> {headers}")
    for i, row in df.iterrows():
        values = row.tolist()
        print(f"i={i}, len={len(values)} -> {values}")


def validate_csv_pandas_by_casting(path):
    pd.read_csv(
        path,
        converters={ "Index": validated_int },
    )


def validated_int(x: str) -> int:
    return int(x)  # pandas will raise a ValueError if this isn't an int


main()
