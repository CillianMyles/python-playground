from pathlib import Path
import polars as pl

BASE = Path(__file__).parent


def maybe_add(
    token: str,
    output_list: list[str],
    max_output_length: int,
    seen_in_this_list: set[str],
    seen_ever: set[str] = set(),
) -> bool:
    if (
        token
        and token not in seen_in_this_list
        and (len(seen_ever) == 0 or token not in seen_ever)
    ):
        seen_in_this_list.add(token)
        seen_ever.add(token)
        output_list.append(token)
        return len(output_list) >= max_output_length
    return False


def generate_single_list_of_unique_names_in_single_file():
    target = 6_000
    unique: set[str] = set()
    ordered: list[str] = []

    male_input = BASE / "data/input/male_names.txt"
    female_input = BASE / "data/input/female_names.txt"
    last_input = BASE / "data/input/last_names.txt"

    with (
        male_input.open("r", encoding="utf-8") as male,
        female_input.open("r", encoding="utf-8") as female,
        last_input.open("r", encoding="utf-8") as last,
    ):
        while len(ordered) < target:
            m_line = male.readline()
            f_line = female.readline()
            l_line = last.readline()

            if not m_line and not f_line and not l_line:
                break  # all files exhausted

            # Parse first token from each line if present
            m_token = (m_line.strip().split() or [None])[0]
            f_token = (f_line.strip().split() or [None])[0]
            l_token = (l_line.strip().split() or [None])[0]

            # Add in the round-robin order, stop as soon as target reached
            if m_token and maybe_add(m_token, ordered, target, unique):
                break
            if f_token and maybe_add(f_token, ordered, target, unique):
                break
            if l_token and maybe_add(l_token, ordered, target, unique):
                break

    print(f"Unique names collected: {len(unique)}")

    output = BASE / "data/output/names.txt"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as file:
        for name in ordered:
            file.write(f"{name}\n")

    print(f'Written to: "{output}"')


def generate_combinations_of_unique_names():
    target_first_names = 3_000
    target_last_names = 3_000
    target_combinations = target_first_names * target_last_names
    print(
        f"TARGETS - first names: {target_first_names}, last names: {target_last_names}, combinations: {target_combinations}"
    )

    unique_first: set[str] = set()
    ordered_first: list[str] = []

    unique_last: set[str] = set()
    ordered_last: list[str] = []

    male_input = BASE / "data/input/male_names.txt"
    female_input = BASE / "data/input/female_names.txt"
    last_input = BASE / "data/input/last_names.txt"

    # First names
    with (
        male_input.open("r", encoding="utf-8") as male,
        female_input.open("r", encoding="utf-8") as file,
    ):
        idx = 0
        while len(ordered_first) < target_first_names:
            m_line = male.readline()
            f_line = file.readline()

            if not m_line and not f_line:
                print("Reached end of first name file(s) early")
                break

            m_token = (m_line.strip().split() or [None])[0]
            f_token = (f_line.strip().split() or [None])[0]
            print(f"[{idx}] male: {m_token}, female: {f_token}")
            idx += 1

            if m_token and maybe_add(
                m_token, ordered_first, target_first_names, unique_first
            ):
                break
            if f_token and maybe_add(
                f_token, ordered_first, target_first_names, unique_first
            ):
                break

    # Last names
    with last_input.open("r", encoding="utf-8") as last:
        while len(ordered_last) < target_last_names:
            l_line = last.readline()
            if not l_line:
                print("Reached end of last name file(s) early")
                break

            l_token = (l_line.strip().split() or [None])[0]
            if l_token and maybe_add(
                l_token, ordered_last, target_last_names, unique_last
            ):
                break

    print(
        f"RESULTS - first names: {len(ordered_first)}, last names: {len(ordered_last)}, combinations: {len(ordered_first) * len(ordered_last)}"
    )

    output = BASE / "data/output/combinations.txt"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as file:
        for first_name in ordered_first:
            for last_name in ordered_last:
                file.write(f"{first_name} {last_name}\n")
    print(f'Wrote TXT file: "{output}"')

    lf_first = pl.LazyFrame({"First": ordered_first})
    lf_last = pl.LazyFrame({"Last": ordered_last})
    lf_combined = lf_first.join(lf_last, how="cross")

    output = BASE / "data/output/combinations.csv"
    lf_combined.sink_csv(output)
    print(f'Wrote CSV file: "{output}"')

    output = BASE / "data/output/combinations.parquet"
    lf_combined.sink_parquet(output, compression="zstd")
    print(f'Wrote Parquet file: "{output}"')


def main():
    # generate_single_list_of_unique_names_in_single_file()
    generate_combinations_of_unique_names()


if __name__ == "__main__":
    main()
