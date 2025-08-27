import csv
import pandas as pd

class StrictDialect(csv.excel):
    delimiter = ","
    quotechar = '"'
    escapechar = "\\"
    doublequote = False
    strict = True

def main():
    print_block("STD / CSV")
    read_csv_std()
    print_block("PANDAS")
    read_csv_pandas()
    validate_csv("data.csv")

def print_block(text):
    print(f"====== {text} ======")

def read_csv_std():
    with open("data.csv", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            print(f"{[len(row)]} {row}")

def read_csv_pandas():
    df = pd.read_csv(
        "data.csv",
        sep=",",
        quotechar='"',
        escapechar=None,
        engine="c",
        on_bad_lines="error",
    )
    columns = df.columns
    print(f"[{len(columns)}] {columns}")
    for _, row in df.iterrows():
        values = row.tolist()
        print(f"[{len(values)}] {values}")

def validate_csv(path: str):
    with open(path, newline="") as f:
        r = csv.reader(f, dialect=StrictDialect)
        header = next(r)
        ncols = len(header)
        if len(header) != ncols:
            raise ValueError(f"Header has {len(header)} cols, expected {ncols}")
        for i, row in enumerate(r, start=2):  # 1-based lines, header=1
            if len(row) != ncols:
                raise ValueError(
                    f"Line {i}: expected {ncols} fields, saw {len(row)} -> {row}"
                )

main()
