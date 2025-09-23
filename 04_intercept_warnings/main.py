from contextlib import contextmanager
import csv
from dataclasses import dataclass
from io import StringIO
import re
from typing import List
import warnings

import pandas as pd


TYPE_HEADER = "header"
TYPE_VALID = "valid"
TYPE_INVALID = "invalid"


@dataclass
class SkippedLine:
    number: int
    reason: str
    raw_message: str

    def __str__(self):
        return f"Line [{self.number}]: {self.reason}"

    def __repr__(self):
        return f'SkippedLine(number={self.number}, reason="{self.reason}", raw_message="{self.raw_message}")'


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
    for warning in warning_list:
        message = str(warning.message)
        # pandas sometimes emits multiple "Skipping line ..." lines in one warning
        for line in message.splitlines():
            match = re.search(r"Skipping line(?:s)?\s+(\d+)\s*:\s*(.+)", line)
            if match:
                skipped_lines.append(
                    SkippedLine(
                        number=int(match.group(1)),
                        reason=match.group(2),
                        raw_message=line,
                    )
                )


@dataclass
class Line:
    number: int
    type: str
    data: list[str]

    def __str__(self):
        return f'Line [{self.number}] - type: "{self.type}" - items[{len(self.data)}]: {self.data}'

    def __repr__(self):
        return f'Line(number={self.number}, type="{self.type}", items={self.data})'


def pre_process_csv(file_path: str) -> list[Line]:
    lines = []

    with open(file_path, newline="") as file:
        reader = csv.reader(file)
        headers = next(reader)
        if headers != _headers:
            raise ValueError(
                f"Headers mismatch... expected {_headers} but got {headers}"
            )

        lines.append(Line(number=0, type=TYPE_HEADER, data=headers))
        num_columns = len(headers)

        for i, row in enumerate(reader, start=1):
            if len(row) != num_columns:
                lines.append(Line(number=i, type=TYPE_INVALID, data=row))
            else:
                lines.append(Line(number=i, type=TYPE_VALID, data=row))

    return lines


def process_csv(file_path: str) -> None:
    lines = pre_process_csv(file_path)
    for line in lines:
        print(line)


def _process_csv(file_path: str) -> None:
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
    pd.read_csv(file_path, **config)
    print_divider()
    print("finished reading CSV outside context manager")

    with log_skipped_lines() as skipped_lines:
        print_spacing()
        print("starting reading CSV inside context manager")
        print_divider()
        pd.read_csv(file_path, **config)
        print_divider()
        print("finished reading CSV inside context manager")

    print_spacing()
    print("processing warnings captured")
    print_divider()

    if skipped_lines:
        print(f"Total invalid lines skipped: {len(skipped_lines)}")

        for skip in skipped_lines:
            print(f"Line {skip.number} skipped because: {skip.reason}")
    else:
        print("No lines were skipped")

    print_spacing()


def main():
    # process_csv(_valid_first_line_path)
    process_csv(_invalid_first_line_path)


_headers = ["Index", "First Name", "Middle Name", "Last Name"]

_valid_first_line_path = "04_intercept_warnings/first_line_valid.csv"
_invalid_first_line_path = "04_intercept_warnings/first_line_invalid.csv"


def print_spacing(lines: int = 2) -> None:
    print_repeated("\n", lines)


def print_divider(char: str = "=", times: int = 50) -> None:
    print_repeated(char, times)


def print_repeated(text: str, times: int) -> None:
    print(text * times)


if __name__ == "__main__":
    main()
