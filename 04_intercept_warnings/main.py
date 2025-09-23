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
    content: str
    items: list[str]

    def __str__(self):
        return f'Line [{self.number}] - type: "{self.type}" - content: "{self.content}" - items[{len(self.items)}]: {self.items}'

    def __repr__(self):
        return f'Line(number={self.number}, type="{self.type}", content="{self.content}", items={self.items})'


def pre_process_csv(file_path: str) -> list[Line]:
    lines = []

    with open(file_path, newline="") as file:
        for i, line in enumerate(file):
            line = line.rstrip("\r\n")
            reader = csv.reader(
                StringIO(line),
                delimiter=",",
                escapechar=None,
                quoting=csv.QUOTE_MINIMAL,
                doublequote=True,
            )
            row = next(reader)

            if i == 0:
                if row != _headers:
                    raise ValueError(
                        f"Headers mismatch... expected {_headers} but got {row}"
                    )
                else:
                    lines.append(
                        Line(number=0, type=TYPE_HEADER, content=line, items=row)
                    )
            elif len(row) != len(_headers):
                lines.append(Line(number=i, type=TYPE_INVALID, content=line, items=row))
            else:
                lines.append(Line(number=i, type=TYPE_VALID, content=line, items=row))

    return lines


def get_csv_config(file_path: str) -> dict:
    lines = pre_process_csv(file_path)

    header = False
    skip_rows = []
    for i, line in enumerate(lines):
        if i == 0 and line.type == TYPE_HEADER:
            header = True
        elif line.type == TYPE_INVALID:
            skip_rows.append(i)
        else:
            break

    config = {
        "delimiter": ",",
        "escapechar": None,
        "quoting": csv.QUOTE_MINIMAL,
        "doublequote": True,
        "on_bad_lines": "warn",
        "names": _headers,
        "header": 0 if header else None,
        "skiprows": skip_rows,
    }

    # === DELIBERATELY PRODUCE ERROR MESSAGE(S) FOR SKIPPED LINES === #
    if skip_rows:
        fake_lines = []
        for line in lines:
            if line.type == TYPE_HEADER:
                fake_lines.append(line)
                break
        for line in lines:
            if line.type == TYPE_VALID:
                fake_lines.append(line)
                break
        for i in skip_rows:
            fake_lines.append(lines[i])
        fake_data = []
        for line in fake_lines:
            print(line)
            fake_data.append(line.content)
        fake_csv = "\n".join(fake_data)
        print("fake_csv:", fake_csv)
        pd.read_csv(
            StringIO(fake_csv),
            delimiter=",",
            escapechar=None,
            quoting=csv.QUOTE_MINIMAL,
            doublequote=True,
            on_bad_lines="warn",
            names=_headers,
            header=0 if header else None,
        )
    # === END === #

    return config


def process_csv(file_path: str) -> None:
    print_spacing()
    print("starting reading CSV outside context manager")
    print_divider()
    config = get_csv_config(file_path)
    pd.read_csv(file_path, **config)
    print_divider()
    print("finished reading CSV outside context manager")

    with log_skipped_lines() as skipped_lines:
        print_spacing()
        print("starting reading CSV inside context manager")
        print_divider()
        config = get_csv_config(file_path)
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
