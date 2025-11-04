import os
from faker import Faker


def generate_and_persist_names(
    per_category: int,
    locale: str = "en_US",
) -> None:
    print(f'Locale: "{locale}"')

    fake = Faker(locale=locale)

    first_names_male = set()
    first_names_female = set()
    last_names = set()

    # Generate random but unique names
    count = 0
    while count < per_category:
        count += 1

        while len(first_names_male) < count:
            name = fake.first_name_male()
            if name.isascii() and name.isalpha():
                first_names_male.add(name)

        while len(first_names_female) < count:
            name = fake.first_name_female()
            if name.isascii() and name.isalpha():
                first_names_female.add(name)

        while len(last_names) < count:
            name = fake.last_name()
            if name.isascii() and name.isalpha():
                last_names.add(name)

    # Persist names to files
    dir = f"{__dir__}/first_names_male"
    file = f"{dir}/{locale}.txt"
    os.makedirs(dir, exist_ok=True)
    with open(file, "w") as f:
        for name in first_names_male:
            f.write(f"{name}\n")
    print(f'Male Names: {len(first_names_male)} written to "{file}"')

    dir = f"{__dir__}/first_names_female"
    file = f"{dir}/{locale}.txt"
    os.makedirs(dir, exist_ok=True)
    with open(file, "w") as f:
        for name in first_names_female:
            f.write(f"{name}\n")
    print(f'Female Names: {len(first_names_female)} written to "{file}"')

    dir = f"{__dir__}/last_names"
    os.makedirs(dir, exist_ok=True)
    file = f"{dir}/{locale}.txt"
    with open(file, "w") as f:
        for name in last_names:
            f.write(f"{name}\n")
    print(f'Last Names: {len(last_names)} written to "{file}"')


def generate_names_for_locales(count: int, locales: list[str]):
    for locale in locales:
        print("-" * 80)
        generate_and_persist_names(count, locale)


def generate_name_files_per_locale():
    generate_names_for_locales(250, ["en_US", "en_CA"])
    generate_names_for_locales(100, ["en_GB", "en_IE", "en_AU"])
    generate_names_for_locales(100, ["es_ES", "es_MX"])
    generate_names_for_locales(75, ["pt_PT", "pt_BR"])
    generate_names_for_locales(50, ["fr_FR", "fr_CA"])
    generate_names_for_locales(100, ["it_IT"])
    generate_names_for_locales(100, ["nl_NL"])
    generate_names_for_locales(100, ["de_DE"])
    generate_names_for_locales(50, ["pl_PL"])


def create_single_names_file():
    names = set()

    dir = f"{__dir__}/first_names_male"
    files = os.listdir(dir)
    for file in files:
        with open(f"{dir}/{file}", "r") as f:
            for line in f:
                names.add(line.strip().upper())

    dir = f"{__dir__}/first_names_female"
    files = os.listdir(dir)
    for file in files:
        with open(f"{dir}/{file}", "r") as f:
            for line in f:
                names.add(line.strip().upper())

    dir = f"{__dir__}/last_names"
    files = os.listdir(dir)
    for file in files:
        with open(f"{dir}/{file}", "r") as f:
            for line in f:
                names.add(line.strip().upper())

    file = f"{__dir__}/names.txt"
    with open(file, "w") as f:
        for name in list(names):
            f.write(f"{name}\n")

    print("-" * 80)
    print(f"Total unique names collected: {len(names)}")
    print(f'Written to: "{file}"')


def main():
    generate_name_files_per_locale()
    create_single_names_file()


__dir__ = "12_create_names_dataset"


if __name__ == "__main__":
    main()
