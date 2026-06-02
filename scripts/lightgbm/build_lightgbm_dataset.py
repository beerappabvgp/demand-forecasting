import polars as pl

from src.models.lightgbm.dataset_builder import (
    LightGBMDatasetBuilder
)


def main():

    print(
        "Loading train dataset"
    )

    train_df = (
        pl.read_parquet(
            "data/training/train_dataset.parquet"
        )
    )

    builder = (
        LightGBMDatasetBuilder()
    )

    print(
        "Building LightGBM dataset"
    )

    model_df = (
        builder.build(
            train_df
        )
    )

    output_path = (
        "data/training/"
        "lightgbm_train_dataset.parquet"
    )

    print(
        "Saving dataset"
    )

    model_df.write_parquet(
        output_path
    )

    print()
    print(
        f"Rows: {model_df.height}"
    )

    print(
        f"Columns: {model_df.width}"
    )

    print()

    print(
        model_df.select(
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