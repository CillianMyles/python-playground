from contextlib import contextmanager
import csv
from dataclasses import dataclass
from io import StringIO
import re
from typing import List
import warnings

import pandas as pd


@dataclass
class SkippedLine:
    line_number: int
    reason: str
    raw_message: str

    def __str__(self):
        return f"Line {self.line_number}: {self.reason}"

    def __repr__(self):
        return f"SkippedLine(line_number={self.line_number}, reason='{self.reason}')"


@contextmanager
def log_skipped_lines():
    """
    Context manager that yields a list of SkippedLine objects.
    Captures pandas ParserWarning messages from read_csv(on_bad_lines="warn").
    """
    skipped_lines: List[SkippedLine] = []
    with warnings.catch_warnings(record=True) as warning_list:
        # only capture the thing we care about
        warnings.filterwarnings("always", category=pd.errors.ParserWarning)
        yield skipped_lines

    # process after the block runs
    for w in warning_list:
        msg = str(w.message)
        # pandas sometimes emits multiple "Skipping line ..." lines in one warning
        for line in msg.splitlines():
            m = re.search(r"Skipping line(?:s)?\s+(\d+)\s*:\s*(.+)", line)
            if m:
                skipped_lines.append(
                    SkippedLine(
                        line_number=int(m.group(1)),
                        reason=m.group(2),
                        raw_message=line,
                    )
                )


def process_csv(file, first_data_line_valid: bool):
    config = {
        "delimiter": ",",
        "escapechar": None,
        "quoting": csv.QUOTE_MINIMAL,
        "doublequote": True,
        "header": None,
        "names": _headers,
        "skiprows": [0] if first_data_line_valid else [0, 1],
        "on_bad_lines": "warn",
    }

    print_spacing()
    print("starting reading CSV outside context manager")
    print_divider()
    pd.read_csv(file, **config)
    print_divider()
    print("finished reading CSV outside context manager")

    with log_skipped_lines() as skipped_lines:
        print_spacing()
        print("starting reading CSV inside context manager")
        print_divider()
        pd.read_csv(file, **config)
        print_divider()
        print("finished reading CSV inside context manager")

    print_spacing()
    print("processing warnings captured")
    print_divider()

    if skipped_lines:
        print(f"Total invalid lines skipped: {len(skipped_lines)}")

        for skip in skipped_lines:
            print(f"Line {skip.line_number} skipped because: {skip.reason}")
    else:
        print("No lines were skipped")

    print_spacing()


def main():
    # process_csv(_valid_first_line_path, first_data_line_valid=True)
    process_csv(_invalid_first_line_path, first_data_line_valid=False)


_headers = ["Index", "First Name", "Middle Name", "Last Name"]

_valid_first_line_path = "04_intercept_warnings/first_line_valid.csv"
_invalid_first_line_path = "04_intercept_warnings/first_line_invalid.csv"

_valid_first_line_csv = StringIO(
    r"""
Index,First Name,Middle Name,Last Name
1,"Mr. Al\, B.",grüBen,Johnson
2,Mr. Al\, B.,grüBen,Johnson
3,\"Mr. Al\, B.\",grüBen,Johnson
4,Mr. Al\, B.,grüBen,Johnson
""".strip()
)

_invalid_first_line_csv = StringIO(
    r"""
Index,First Name,Middle Name,Last Name
1,Mr. Al\, B.,grüBen,Johnson
2,"Mr. Al\, B.",grüBen,Johnson
3,\"Mr. Al\, B.\",grüBen,Johnson
4,Mr. Al\, B.,grüBen,Johnson
""".strip()
)


def print_spacing(lines: int = 2) -> None:
    print_repeated("\n", lines)


def print_divider(char: str = "=", times: int = 50) -> None:
    print_repeated(char, times)


def print_repeated(text: str, times: int) -> None:
    print(text * times)


if __name__ == "__main__":
    main()
