from faker import Faker


def generate_and_persist_names(
    per_category: int,
    locale: str = "en_US",
) -> None:
    print("-" * 80)
    print("Locale:", locale)

    fake = Faker(locale=locale)

    first_names_male = set()
    first_names_female = set()
    last_names = set()

    # Generate random but unique names
    count = 0
    while count < per_category:
        count += 1
        while len(first_names_male) < count:
            first_names_male.add(fake.first_name_male())
        while len(first_names_female) < count:
            first_names_female.add(fake.first_name_female())
        while len(last_names) < count:
            last_names.add(fake.last_name())

    # Persist names to files
    with open(f"{__directory__}/first_names_male/{locale}.txt", "w") as f:
        for name in sorted(first_names_male):
            f.write(f"{name}\n")
    with open(f"{__directory__}/first_names_female/{locale}.txt", "w") as f:
        for name in sorted(first_names_female):
            f.write(f"{name}\n")
    with open(f"{__directory__}/last_names/{locale}.txt", "w") as f:
        for name in sorted(last_names):
            f.write(f"{name}\n")

    print("First Names (Male):", len(first_names_male))
    print("First Names (Female):", len(first_names_female))
    print("Last Names:", len(last_names))


def generate_names_for_locale(count: int, locales: list[str]):
    for locale in locales:
        generate_and_persist_names(count, locale)


def generate_names_data():
    generate_names_for_locale(250, ["en_US", "en_CA"])
    generate_names_for_locale(100, ["en_GB", "en_IE", "en_AU"])
    generate_names_for_locale(100, ["es_ES", "es_MX"])
    generate_names_for_locale(75, ["pt_PT", "pt_BR"])
    generate_names_for_locale(75, ["fr_FR", "fr_CA"])
    generate_names_for_locale(100, ["it_IT"])
    generate_names_for_locale(100, ["nl_NL"])
    generate_names_for_locale(100, ["de_DE"])
    generate_names_for_locale(50, ["pl_PL"])
    generate_names_for_locale(75, ["ru_RU"])


def main():
    generate_names_data()


__directory__ = "12_create_names_dataset"


if __name__ == "__main__":
    main()
