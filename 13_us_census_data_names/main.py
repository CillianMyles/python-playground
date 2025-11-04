from pathlib import Path

BASE = Path(__file__).parent


def add_if_new(token: str, seen: set[str], out: list[str], target: int) -> bool:
    if token and token not in seen:
        seen.add(token)
        out.append(token)
        return len(out) >= target
    return False


def main():
    target = 6_000
    unique: set[str] = set()
    ordered: list[str] = []

    male_p = BASE / "data/input/male_names.txt"
    female_p = BASE / "data/input/female_names.txt"
    last_p = BASE / "data/input/last_names.txt"

    with (
        male_p.open("r", encoding="utf-8") as m,
        female_p.open("r", encoding="utf-8") as f,
        last_p.open("r", encoding="utf-8") as l,
    ):
        while len(ordered) < target:
            m_line = m.readline()
            f_line = f.readline()
            l_line = l.readline()

            if not m_line and not f_line and not l_line:
                break  # all files exhausted

            # Parse first token from each line if present
            m_token = (m_line.strip().split() or [None])[0]
            f_token = (f_line.strip().split() or [None])[0]
            l_token = (l_line.strip().split() or [None])[0]

            # Add in the round-robin order, stop as soon as target reached
            if m_token and add_if_new(m_token, unique, ordered, target):
                break
            if f_token and add_if_new(f_token, unique, ordered, target):
                break
            if l_token and add_if_new(l_token, unique, ordered, target):
                break

    print(f"Unique names collected: {len(unique)}")

    out_p = BASE / "data/output/names.txt"
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with out_p.open("w", encoding="utf-8", newline="\n") as f:
        for name in ordered:
            f.write(f"{name}\n")

    print(f'Written to: "{out_p}"')


if __name__ == "__main__":
    main()
