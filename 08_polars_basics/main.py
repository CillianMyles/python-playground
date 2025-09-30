import polars as pl


def main():
    plan = pl.LazyFrame(
        {
            "name": ["Batman", "Gandalf"],
            "age": [35, 42999],
        }
    )
    print("plan:", plan)

    all = plan.collect()
    print("all:", all)

    # filtering rows by where value for "age" column is more than 35
    old = plan.filter(pl.col("age") > 35).collect()
    print("old:", old)

    # selecting the sum of all age values
    selected = plan.select(pl.col("age").sum()).collect()
    print("selected:", selected)


if __name__ == "__main__":
    main()
