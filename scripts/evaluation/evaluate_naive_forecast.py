import polars as pl
import math

from src.models.baseline.naive_forecaster import (
    NaiveForecaster
)


def main():

    print(
        "Loading validation dataset"
    )

    validation_df = (
        pl.read_parquet(
            "data/training/validation_dataset.parquet"
        )
    )

    forecaster = (
        NaiveForecaster()
    )

    print(
        "Generating predictions"
    )

    prediction_df = (
        forecaster.predict(
            validation_df
        )
    )

    print(
        "Calculating MAE"
    )

    mae = (
        prediction_df
        .select(
            (
                (
                    pl.col("sales")
                    -
                    pl.col("prediction")
                )
                .abs()
                .mean()
            )
            .alias("mae")
        )
        .item()
    )

    print(
        "Calculating RMSE"
    )

    mse = (
        prediction_df
        .select(
            (
                (
                    pl.col("sales")
                    -
                    pl.col("prediction")
                )
                ** 2
            )
            .mean()
            .alias("mse")
        )
        .item()
    )

    rmse = math.sqrt(
        mse
    )

    print()
    print(
        f"MAE  : {mae:.4f}"
    )

    print(
        f"RMSE : {rmse:.4f}"
    )


if __name__ == "__main__":
    main()