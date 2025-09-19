from typing import Any


def print_it(name: str, it: Any) -> None:
    if isinstance(it, list):
        print(f"{name}: [len={len(it)}]: {it}")
    elif isinstance(it, str):
        print(f'{name}: "{it}"')
    else:
        print(f"{name}: {it}")


def main() -> None:
    fruits = ["apple", "banana", "cherry"]
    print_it("\nfruits", fruits)

    empty = []
    print_it("\nempty", empty)

    numbers = [1, 2, 3, 4, 5]
    print_it("\nnumbers", numbers)

    mixed = [1, "two", 3.0, True, None]
    print_it("\nmixed", mixed)

    single = ["only_one"]
    print_it("\nsingle", single)

    string = "just a string"
    print_it("\nstring", string)

    integer = 42
    print_it("\ninteger", integer)

    float = 3.14
    print_it("\nfloat", float)


if __name__ == "__main__":
    main()
