from metaphone import metaphone

def main():
    print(metaphone("input"))
    print(soundex("input"))


def soundex(input: str) -> str:
    return f"soundex_{input}"


if __name__ == "__main__":
    main()
