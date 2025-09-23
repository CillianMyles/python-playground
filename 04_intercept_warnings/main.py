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
class Line:
    number: int
    type: str
    content: str
    items: list[str]

    def __str__(self):
        return f'Line [{self.number}] - type: "{self.type}" - content: "{self.content}" - items[{len(self.items)}]: {self.items}'

    def __repr__(self):
        return f'Line(number={self.number}, type="{self.type}", content="{self.content}", items={self.items})'


@dataclass
class SkippedLine:
    number: int
    reason: str

    def __str__(self):
        return f"Line [{self.number}]: {self.reason}"

    def __repr__(self):
        return f'SkippedLine(number={self.number}, reason="{self.reason}")'


@contextmanager
def watch_skipped_line_warnings():
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
                    )
                )


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


def get_csv_config(file_path: str):
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

    skipped_lines = None
    if skip_rows:
        skipped_lines = []
        for i in skip_rows:
            line = lines[i]
            skipped_line = SkippedLine(
                number=line.number,
                reason=f"expected {len(_headers)} fields, saw {len(line.items)}",
            )
            skipped_lines.append(skipped_line)

    return skipped_lines, config


def process_csv(input_path: str, output_path: str) -> None:
    with open(output_path, "w") as output_file:
        with watch_skipped_line_warnings() as warned_lines:
            skipped_lines, config = get_csv_config(input_path)
            pd.read_csv(input_path, **config)

        invalid_lines = []
        if skipped_lines:
            invalid_lines.extend(skipped_lines)
        if warned_lines:
            invalid_lines.extend(warned_lines)

        if invalid_lines:
            output_file.write(f"Total invalid lines skipped: {len(invalid_lines)}\n")
            for skip in invalid_lines:
                output_file.write(
                    f"Line {skip.number} skipped because: {skip.reason}\n"
                )
        else:
            output_file.write("No lines were skipped\n")


def main():
    process_csv(
        input_path="04_intercept_warnings/first_line_valid.csv",
        output_path="04_intercept_warnings/output_first_line_valid.log",
    )
    process_csv(
        input_path="04_intercept_warnings/first_line_invalid.csv",
        output_path="04_intercept_warnings/output_first_line_invalid.log",
    )


_headers = ["Index", "First Name", "Middle Name", "Last Name"]


if __name__ == "__main__":
    main()
