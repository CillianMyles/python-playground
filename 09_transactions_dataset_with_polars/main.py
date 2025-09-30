import polars as pl


def main():
    # read directly from csv file
    data = pl.scan_csv(f"{__dir__}/transactions.csv")
    print("data schema:", data.collect_schema())
    print("data head:", data.head().collect())

    # query the number of entries by unique customer ids
    distinct_customers = data.select(pl.col("CustomerID").n_unique()).collect()
    print("distinct_customers:", distinct_customers)

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
    bar_chart = best_performing_categories.plot.bar(
        x="ProductCategory",
        y="Total",
    ).properties(
        width=500,
        title="Best Performing Product Categories",
    )
    bar_chart.save(f"{__dir__}/bar.png")

    # scatter plot of transactions
    scatter_chart = (
        data.collect()
        .plot.scatter(
            x="TotalAmount",
            y="TransactionDate",
            color="ProductCategory",
        )
        .properties(
            width=750,
            title="Transactions",
        )
    )
    scatter_chart.save(f"{__dir__}/scatter.png")


__dir__ = "09_transactions_dataset_with_polars"


if __name__ == "__main__":
    main()
