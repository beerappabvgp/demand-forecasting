import polars as pl


class NaiveForecaster:

    def predict(
        self,
        dataset: pl.DataFrame
    ) -> pl.DataFrame:

        return (
            dataset
            .filter(
                pl.col("lag_1").is_not_null()
            )
            .with_columns(
                pl.col("lag_1")
                .alias("prediction")
            )
        )