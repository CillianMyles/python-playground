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
    )
    print("\nbasic_select_and_transform")
    print("plan:", basic_select_and_transform.explain(optimized=True))
    print("df:", basic_select_and_transform.collect())

    # grouping and aggregation
    basic_grouping_and_aggregation = (
        data.group_by(["Survived", "Pclass"])
        .agg(pl.col("PassengerId").count().alias("counts"))
        .sort(by=["Pclass", "Survived"], descending=[False, False])
    )
    print("\nbasic_grouping_and_aggregation")
    print("plan:", basic_grouping_and_aggregation.explain(optimized=True))
    print("df:", basic_grouping_and_aggregation.collect())


__dir__ = "10_more_polars"


if __name__ == "__main__":
    main()
