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
    data = pl.scan_csv(f"{__dir__}/transactions.csv")
    print("schema:", data.collect_schema())
    print("head:", data.head().collect())

    # query the number of entries by unique customer ids
    num_customers = data.select(pl.col("CustomerID").n_unique()).collect()
    print("num_customers:", num_customers)

    # combine filter, select, and sum
    books_totals = (
        data.filter(
            (pl.col("ProductCategory") == "Books")
            & (pl.col("DiscountApplied(%)") <= 10.0)
        )
        .select(pl.sum("TotalAmount"))
        .collect()
    )
    print("books_totals:", books_totals)

    # list product catgories which have the biggest total amounts spent cummulatively
    best_performing_categories = (
        data.group_by("ProductCategory")
        .agg(
            pl.sum("TotalAmount").alias("Total"),
            pl.mean("TotalAmount").alias("Average"),
            pl.count("TotalAmount").alias("Count"),
        )
        .sort(by="Total", descending=True)
        .collect()
    )
    print("best_performing_categories:", best_performing_categories)

    # graph the previous data frame/set
    bar = best_performing_categories.plot.bar(
        x="ProductCategory",
        y="Total",
    ).properties(width=500)
    bar.save(f"{__dir__}/bar.png")

    # scatter
    scatter = (
        data.collect()
        .plot.scatter(
            x="TotalAmount",
            y="TransactionDate",
            color="ProductCategory",
        )
        .properties(width=750)
    )
    scatter.save(f"{__dir__}/scatter.png")


__dir__ = "08_exploring_polars"


if __name__ == "__main__":
    main()
