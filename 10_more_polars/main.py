import polars as pl


def main():
    # read directly from csv file
    data = pl.scan_csv(f"{__dir__}/titanic.csv")
    print("data schema:", data.collect_schema())
    print("data head:", data.head().collect())

    # select some columns and apply basic transformations
    basic_select_and_transform = data.select(
        pl.col("Pclass"),
        pl.col("Name").str.to_lowercase(),
        pl.col("Age").round(2),
    ).collect()
    print("basic_select_and_transform:", basic_select_and_transform)

    # grouping and aggregation
    basic_grouping_and_aggregation = (
        data.group_by(["Survived", "Pclass"])
        .agg(pl.col("PassengerId").count().alias("counts"))
        .sort(by="Survived", descending=False)
        .sort(by="Pclass", descending=False)
        .collect()
    )
    print("basic_grouping_and_aggregation:", basic_grouping_and_aggregation)


__dir__ = "10_more_polars"


if __name__ == "__main__":
    main()
