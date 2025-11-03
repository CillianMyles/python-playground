from faker import Faker


def generate_names(
    names_per_category: int,
    locale: str = "en_US",
) -> None:
    print("-" * 80)
    print("Locale:", locale)

    fake = Faker(locale=locale)

    first_names_male = set()
    first_names_female = set()
    first_names_neutral = set()
    last_names = set()

    # Generate random but unique names
    count = 0
    while count < names_per_category:
        count += 1
        while len(first_names_male) < count:
            first_names_male.add(fake.first_name_male())
        while len(first_names_female) < count:
            first_names_female.add(fake.first_name_female())
        while len(first_names_neutral) < count:
            first_names_neutral.add(fake.first_name_nonbinary())
        while len(last_names) < count:
            last_names.add(fake.last_name())

    # Persist names to files
    with open(f"{__directory__}/first_names_male/{locale}.txt", "w") as f:
        for name in sorted(first_names_male):
            f.write(f"{name}\n")
    with open(f"{__directory__}/first_names_female/{locale}.txt", "w") as f:
        for name in sorted(first_names_female):
            f.write(f"{name}\n")
    with open(f"{__directory__}/first_names_neutral/{locale}.txt", "w") as f:
        for name in sorted(first_names_neutral):
            f.write(f"{name}\n")
    with open(f"{__directory__}/last_names/{locale}.txt", "w") as f:
        for name in sorted(last_names):
            f.write(f"{name}\n")
    
    print("First Names (Male):", len(first_names_male))
    print("First Names (Female):", len(first_names_female))
    print("First Names (Neutral):", len(first_names_neutral))
    print("Last Names:", len(last_names))


def main():
    names_per_category = 100
    locales = ["en_US", "en_GB", "es_ES", "de_DE"]

    for locale in locales:
        generate_names(names_per_category, locale)


__directory__ = "12_create_names_dataset"


if __name__ == "__main__":
    main()
