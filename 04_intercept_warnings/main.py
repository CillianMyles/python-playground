from __future__ import annotations

from contextlib import contextmanager
import csv
from dataclasses import dataclass
from enum import StrEnum
from io import StringIO
from pathlib import Path
import re
from typing import List, Literal, TypedDict
import warnings

import pandas as pd


class LineType(StrEnum):
    HEADER = "header"
    VALID = "valid"
    INVALID = "invalid"


@dataclass(slots=True, frozen=True)
class Line:
    number: int  # 1-based file line number
    type: LineType
    content: str
    items: list[str]

    def __str__(self) -> str:
        return f'Line [{self.number}] - type: "{self.type}" - content: "{self.content}" - items[{len(self.items)}]: {self.items}'


@dataclass(slots=True, frozen=True)
class SkippedLine:
    number: int  # 1-based file line number
    reason: str

    def __str__(self) -> str:
        return f'Line [{self.number}] - reason: "{self.reason}"'


BadLines = Literal["warn", "error", "skip"]


class CsvConfig(TypedDict):
    delimiter: str
    escapechar: str | None
    quoting: int
    doublequote: bool
    on_bad_lines: BadLines
    names: list[str]
    header: int | None
    skiprows: list[int]


_SKIP_RE = re.compile(r"Skipping line(?:s)?\s+([0-9,\s]+)\s*:\s*(.+)")


@contextmanager
def watch_skipped_line_warnings():
    """
    Yields a list of SkippedLine (1-based line numbers).
    Collects pandas ParserWarning from read_csv(on_bad_lines="warn") after the with-block.
    """
    collected: List[SkippedLine] = []

    with warnings.catch_warnings(record=True) as warningz:
        warnings.filterwarnings("always", category=pd.errors.ParserWarning)
        yield collected

    for warning in warningz:
        message = str(warning.message)
        for line in message.splitlines():
            if matches := _SKIP_RE.search(line):
                numbers = [int(s) for s in matches.group(1).replace(" ", "").split(",") if s]
                reason = matches.group(2)
                collected.extend(SkippedLine(number=n, reason=reason) for n in numbers)


def pre_process_csv(file_path: Path | str, headers: list[str]) -> list[Line]:
    """
    Lightweight pre-scan to identify header and per-line field counts.
    1-based line numbers for human readability.
    """
    path = Path(file_path)
    lines: list[Line] = []

    with path.open("r", encoding="utf-8", newline="") as file:
        for i, raw in enumerate(file, start=1):  # 1-based
            line = raw.rstrip("\r\n")
            row = next(
                csv.reader(
                    StringIO(line),
                    delimiter=",",
                    escapechar=None,
                    quoting=csv.QUOTE_MINIMAL,
                    doublequote=True,
                ),
                [],
            )

            if i == 1:  # 1-based
                if row != headers:
                    raise ValueError(
                        f"Header mismatch: expected {headers!r} but got {row!r}"
                    )
                lines.append(
                    Line(number=i, type=LineType.HEADER, content=line, items=row)
                )
            elif len(row) != len(headers):
                lines.append(
                    Line(number=i, type=LineType.INVALID, content=line, items=row)
                )
            else:
                lines.append(
                    Line(number=i, type=LineType.VALID, content=line, items=row)
                )

    return lines


def get_csv_config(
    file_path: Path | str, headers: list[str]
) -> tuple[list[SkippedLine] | None, CsvConfig]:
    lines = pre_process_csv(file_path, headers)

    # Collect only the *leading* invalid lines (before the first valid after header)
    has_header = len(lines) > 0 and lines[0].type is LineType.HEADER
    skip_rows_0_based: list[int] = []

    for i, line in enumerate(lines, start=1):  # i is 1-based index into file
        if i == 1 and line.type is LineType.HEADER:
            continue
        if line.type is LineType.INVALID:
            skip_rows_0_based.append(line.number - 1) # pandas expects 0-based row indices
        else:
            break

    config: CsvConfig = {
        "delimiter": ",",
        "escapechar": None,
        "quoting": csv.QUOTE_MINIMAL,
        "doublequote": True,
        "on_bad_lines": "warn",
        "names": headers,
        "header": 0 if has_header else None,
        "skiprows": skip_rows_0_based,
    }

    skipped_lines: list[SkippedLine] | None = None
    if skip_rows_0_based:
        skipped_lines = [
            SkippedLine(
                number=i + 1,  # back to 1-based
                reason=f"expected {len(headers)} fields, saw {len(lines[i].items)}",
            )
            for i in skip_rows_0_based
        ]

    return skipped_lines, config


def process_csv(
    input_path: Path | str, output_path: Path | str, headers: list[str]
) -> None:
    path = Path(output_path)

    with path.open("w", encoding="utf-8", newline="\n") as file:
        with watch_skipped_line_warnings() as warned_lines:
            skipped_lines, config = get_csv_config(input_path, headers)
            pd.read_csv(input_path, **config)

        invalid: list[SkippedLine] = []
        if skipped_lines:
            invalid.extend(skipped_lines)
        if warned_lines:
            invalid.extend(warned_lines)

        if invalid:
            file.write(f"Total invalid lines skipped: {len(invalid)}\n")
            for sl in invalid:
                file.write(f"Line {sl.number} skipped because: {sl.reason}\n")
        else:
            file.write("No lines were skipped\n")


def main() -> None:
    HEADERS = ["Index", "First Name", "Middle Name", "Last Name"]

    process_csv(
        input_path=Path("04_intercept_warnings/first_line_valid.csv"),
        output_path=Path("04_intercept_warnings/output_first_line_valid.log"),
        headers=HEADERS,
    )

    process_csv(
        input_path=Path("04_intercept_warnings/first_line_invalid.csv"),
        output_path=Path("04_intercept_warnings/output_first_line_invalid.log"),
        headers=HEADERS,
    )


if __name__ == "__main__":
    main()
