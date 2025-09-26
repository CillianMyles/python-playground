from pathlib import Path


def duplicate_file(
    input_path: str | Path,
    output_path: str | Path,
    lines_in_output: int,
) -> None:
    """
    Duplicates the contents of the input file to the output file.

    If lines_in_output is less than the number of lines in the input file, only the specified number of lines will be written to the output file.

    If lines_in_output is greater than the number of lines in the input file, the contents of the input file will be duplicated until the output file reaches the specified number of lines.

    Args:
        input_path (str | Path): Path to the input file.
        output_path (str | Path): Path to the output file.
        lines_in_output (int): Number of lines to write to the output file.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    with input_path.open("r") as in_file, output_path.open("w") as out_file:
        lines = list(in_file.readlines())
        if not lines:
            raise ValueError(f'Input file "{input_path}" is empty.')

        while True:
            for line in lines:
                if lines_in_output <= 0:
                    return
                out_file.write(line)
                lines_in_output -= 1


def main():
    duplicate_file(
        input_path="07_duplicate_file/10_lines.txt",
        output_path="07_duplicate_file/3_lines.txt",
        lines_in_output=3,
    )
    duplicate_file(
        input_path="07_duplicate_file/3_lines.txt",
        output_path="07_duplicate_file/9_lines.txt",
        lines_in_output=9,
    )
    duplicate_file(
        input_path="07_duplicate_file/10_lines.txt",
        output_path="07_duplicate_file/101_lines.txt",
        lines_in_output=101,
    )


if __name__ == "__main__":
    main()
