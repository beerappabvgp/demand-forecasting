from pathlib import Path

import polars as pl

from src.common.logger import logger


class TrainingDatasetBuilder:

    RECENT_WINDOW_DAYS = 365

    def build(
        self,
        sales_path: Path,
        calendar_path: Path,
        price_path: Path,
        output_path: Path
    ) -> Path:

        logger.info(
            "Loading sales dataset"
        )

        sales_df = (
            pl.scan_parquet(
                sales_path
            )
        )

        logger.info(
            "Creating day number"
        )

        sales_df = (

            sales_df.with_columns(

                pl.col("day")
                .str.replace("d_", "")
                .cast(pl.Int32)
                .alias("day_number")
            )
        )

        logger.info(
            "Finding latest day"
        )

        latest_day = (

            sales_df
            .select(
                pl.max("day_number")
            )
            .collect()
            .item()
        )

        cutoff_day = (
            latest_day
            - self.RECENT_WINDOW_DAYS
        )

        logger.info(
            f"Latest day: {latest_day}"
        )

        logger.info(
            f"Cutoff day: {cutoff_day}"
        )

        logger.info(
            "Filtering recent window"
        )

        sales_df = (

            sales_df.filter(
                pl.col("day_number")
                >= cutoff_day
            )
        )

        logger.info(
            "Loading calendar dataset"
        )

        calendar_df = (
            pl.scan_parquet(
                calendar_path
            )
        )

        logger.info(
            "Loading price dataset"
        )

        price_df = (
            pl.scan_parquet(
                price_path
            )
        )

        logger.info(
            "Joining calendar"
        )

        dataset = (

            sales_df.join(
                calendar_df,
                on="day",
                how="left"
            )
        )

        logger.info(
            "Joining prices"
        )

        dataset = (

            dataset.join(

                price_df,

                on=[
                    "item_id",
                    "store_id",
                    "wm_yr_wk"
                ],

                how="left"
            )
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        logger.info(
            "Writing training dataset"
        )

        dataset.collect().write_parquet(
            output_path
        )

        logger.info(
            f"Saved dataset: "
            f"{output_path}"
        )

        return output_path