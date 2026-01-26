import csv
import argparse
import sys
from pathlib import Path
from typing import List


def extract_values(csv_file: Path, column: str) -> List[str]:
    values = []
    try:
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if column not in reader.fieldnames:
                print(
                    f"❌ Column '{column}' not found in CSV headers: {reader.fieldnames}",
                    file=sys.stderr,
                )
                return []
            for row in reader:
                value = row.get(column, "").strip()
                if value:
                    values.append(value)
    except FileNotFoundError:
        print(f"❌ File not found: {csv_file}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}", file=sys.stderr)
    return values


def output_values(values: List[str], separator: str, out_file: Path | None):
    joined = f"{separator.strip()} ".join(values)
    if out_file:
        try:
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(joined)
            print(f"✅ Wrote {len(values)} values to {out_file}")
        except Exception as e:
            print(f"❌ Error writing to file: {e}", file=sys.stderr)
    else:
        print(joined)
        print(f"\n✅ Printed {len(values)} values to console")


def main():
    parser = argparse.ArgumentParser(
        description="Extract values from a specified CSV column and output as a separated list"
    )
    parser.add_argument("csv_file", type=Path, help="Path to the input CSV file")
    parser.add_argument(
        "-c", "--column", required=True, help="Header name of the column to extract"
    )
    parser.add_argument(
        "-s",
        "--separator",
        default=",",
        help="Separator to join extracted values (default: ',')",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path (optional; if omitted prints to stdout)",
    )

    args = parser.parse_args()

    values = extract_values(args.csv_file, args.column)
    if not values:
        print(
            "⚠️ No values extracted — check CSV path and column name.", file=sys.stderr
        )
        return

    output_values(values, args.separator, args.output)


if __name__ == "__main__":
    main()
