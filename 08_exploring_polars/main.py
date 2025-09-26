import polars as pl


def main():
    plan = pl.LazyFrame(
        {
            "name": ["Batman", "Gandalf"],
            "age": [35, 42999],
        }
    )
    print("plan:", plan)

    all_df = plan.collect()
    print("all_df:", all_df)

    # filtering rows by where value for "age" column is more than 35
    old_df = plan.filter(pl.col("age") > 100).collect()
    print("old_df:", old_df)

    # selecting the sum of all age values
    select_df = plan.select(pl.col("age").sum()).collect()
    print("select_df:", select_df)

    # read directly from csv file
    data = pl.scan_csv("08_exploring_polars/retail_transactions.csv")
    print("schema:", data.collect_schema())
    print("head:", data.head().collect())

    # query the number of entries by unique customer ids
    num_customers = data.select(pl.col("CustomerID").n_unique()).collect()
    print("num_customers:", num_customers)


if __name__ == "__main__":
    main()
