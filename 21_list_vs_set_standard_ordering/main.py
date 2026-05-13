def main():
    values = [0, 2, 2, 1, 0]
    deduped = set(values)
    sorted = list(dict.fromkeys(values))
    print(f"values: {values}")
    print(f"deduped: {deduped}")
    print(f"sorted: {sorted}")


if __name__ == "__main__":
    main()
