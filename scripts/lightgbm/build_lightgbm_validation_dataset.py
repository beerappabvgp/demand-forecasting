import polars as pl

from src.models.lightgbm.dataset_builder import (
    LightGBMDatasetBuilder
)


def main():

    print(
        "Loading validation dataset"
    )

    df = pl.read_parquet(
        "data/training/validation_dataset.parquet"
    )

    builder = (
        LightGBMDatasetBuilder()
    )

    print(
        "Creating target column"
    )

    result = (
        builder.build(df)
    )

    output_path = (
        "data/training/"
        "lightgbm_validation_dataset.parquet"
    )

    print(
        "Saving dataset"
    )

    result.write_parquet(
        output_path
    )

    print()

    print(
        f"Rows: {result.height}"
    )

    print(
        f"Columns: {result.width}"
    )

    print()

    print(
        result.select(
            [
                "sales",
                "target_sales"
            ]
        ).head(10)
    )

    print()

    print(
        f"Saved: {output_path}"
    )


if __name__ == "__main__":
    main()