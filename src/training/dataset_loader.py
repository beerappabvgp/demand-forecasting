import polars as pl


class DatasetLoader:

    def load_training_data(
        self,
        path: str
    ) -> pl.DataFrame:

        df = (
            pl.read_parquet(path)
            .filter(
                pl.col("lag_28")
                .is_not_null()
            )
        )

        df = (
            df
            .with_columns(
                pl.col("sales")
                .shift(-1)
                .over(
                    [
                        "item_id",
                        "store_id"
                    ]
                )
                .alias(
                    "target_sales"
                )
            )
        )

        df = (
            df
            .filter(
                pl.col("target_sales")
                .is_not_null()
            )
        )

        return df

    def load_validation_data(
        self,
        path: str
    ) -> pl.DataFrame:

        df = (
            pl.read_parquet(path)
            .filter(
                pl.col("lag_28")
                .is_not_null()
            )
        )

        df = (
            df
            .with_columns(
                pl.col("sales")
                .shift(-1)
                .over(
                    [
                        "item_id",
                        "store_id"
                    ]
                )
                .alias(
                    "target_sales"
                )
            )
        )

        df = (
            df
            .filter(
                pl.col("target_sales")
                .is_not_null()
            )
        )

        return df