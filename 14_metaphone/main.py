from metaphone import doublemetaphone


def metaphone(name: str) -> None:
    result = doublemetaphone(name)
    print(f"'{name}' -> {result}")


def main() -> None:
    metaphone("hugh")
    metaphone("hughes")
    metaphone("high")
    metaphone("hightower")


if __name__ == "__main__":
    main()
