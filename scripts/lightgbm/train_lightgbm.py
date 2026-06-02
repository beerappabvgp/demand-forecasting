import polars as pl
import pandas as pd

from src.models.lightgbm.trainer import (
    LightGBMTrainer
)


def main():

    print(
        "Loading dataset"
    )

    df = (
        pl.read_parquet(
            "data/training/lightgbm_train_dataset.parquet"
        )
        .filter(
            pl.col("lag_28")
            .is_not_null()
        )
        .head(100000)
    )

    print(
        f"Rows: {df.height}"
    )

    print(
        "Converting to pandas"
    )

    pandas_df = (
        df.to_pandas()
    )

    trainer = (
        LightGBMTrainer()
    )

    print(
        "Training model"
    )

    model = (
        trainer.train(
            pandas_df
        )
    )

    print()
    print(
        "Training completed"
    )

    print(
        model
    )


if __name__ == "__main__":
    main()