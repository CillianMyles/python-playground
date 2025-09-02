import csv
import pandas as pd

class StrictDialect(csv.excel):
    delimiter = ","
    quotechar = '"'
    escapechar = None
    doublequote = False
    strict = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL

def main():
    file = "data.csv"
    print_block("Read (STD/CSV)")
    read_csv_std(file)
    print_block("Read (PANDAS)")
    read_csv_pandas(file)
    print_block("Validate (STD/CSV)")
    validate_csv_std(file)
    print_block("Validate (PANDAS)")
    validate_csv_pandas(file)

def print_block(text):
    print(f"====== {text} ======")

def read_csv_std(path):
    with open(path, newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            print(f"{[len(row)]} {row}")

def read_csv_pandas(path):
    df = pd.read_csv(
        path,
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

def validate_csv_std(path):
    with open(path, newline="") as file:
        reader = csv.reader(file)
        headers = next(reader)
        num_columns = len(headers)
        for i, row in enumerate(reader, start=2):  # 1-based lines, header=1
            if len(row) != num_columns:
                print(
                    f"Line {i} - ❌ - expected {num_columns} fields, saw {len(row)} -> {row}"
                )
            else:
                print(f"Line {i} - ✅ - OK")

def validate_csv_pandas(path):
    pd.read_csv(
        path,
        converters={ "Index": validated_int },
    )

def validated_int(x: str) -> int:
    # explode early if the Index column isn't actually an integer
    return int(x)  # ValueError -> pandas raises

main()
