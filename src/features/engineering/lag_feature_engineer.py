from pathlib import Path

import polars as pl

from src.common.logger import logger


class LagFeatureEngineer:

    def build(
        self,
        input_path: Path,
        output_path: Path
    ) -> Path:

        logger.info(
            "Loading training dataset"
        )

        df = pl.read_parquet(
            input_path
        )

        logger.info(
            "Sorting dataset"
        )

        df = df.sort(
            [
                "item_id",
                "store_id",
                "day_number"
            ]
        )

        logger.info(
            "Creating lag features"
        )

        df = df.with_columns(

            pl.col("sales")
            .shift(1)
            .over(
                ["item_id", "store_id"]
            )
            .alias("lag_1"),

            pl.col("sales")
            .shift(7)
            .over(
                ["item_id", "store_id"]
            )
            .alias("lag_7"),

            pl.col("sales")
            .shift(28)
            .over(
                ["item_id", "store_id"]
            )
            .alias("lag_28")
        )

        logger.info(
            "Creating rolling features"
        )

        shifted_sales = (
            pl.col("sales")
            .shift(1)
            .over(
                ["item_id", "store_id"]
            )
        )

        df = df.with_columns(

            shifted_sales
            .rolling_mean(
                window_size=7
            )
            .over(
                ["item_id", "store_id"]
            )
            .alias(
                "rolling_mean_7"
            ),

            shifted_sales
            .rolling_mean(
                window_size=28
            )
            .over(
                ["item_id", "store_id"]
            )
            .alias(
                "rolling_mean_28"
            ),

            shifted_sales
            .rolling_std(
                window_size=7
            )
            .over(
                ["item_id", "store_id"]
            )
            .alias(
                "rolling_std_7"
            ),

            shifted_sales
            .rolling_std(
                window_size=28
            )
            .over(
                ["item_id", "store_id"]
            )
            .alias(
                "rolling_std_28"
            )
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        logger.info(
            "Writing feature dataset"
        )

        df.write_parquet(
            output_path
        )

        logger.info(
            f"Saved feature dataset: "
            f"{output_path}"
        )

        return output_path