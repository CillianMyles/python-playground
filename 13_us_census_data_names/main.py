def main():
    target = 6_000
    names = set()

    with (
        open(f"{__dir__}/data/input/male_names.txt", "r") as m,
        open(f"{__dir__}/data/input/female_names.txt", "r") as f,
        open(f"{__dir__}/data/input/last_names.txt", "r") as l,
    ):
        while len(names) < target:
            male = m.readline().strip().split()
            female = f.readline().strip().split()
            last = l.readline().strip().split()

            if male:
                names.add(male[0])
            if female:
                names.add(female[0])
            if last:
                names.add(last[0])

    print(f"Unique names collected: {len(names)}")

    file = f"{__dir__}/data/output/names.txt"
    with open(file, "w") as f:
        for name in sorted(list(names)):
            f.write(f"{name}\n")

    print(f'Written to: "{file}"')


__dir__ = "13_us_census_data_names"


if __name__ == "__main__":
    main()
