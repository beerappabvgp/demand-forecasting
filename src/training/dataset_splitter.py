from pathlib import Path

import polars as pl

from src.common.logger import logger


class DatasetSplitter:

    def split(
        self,
        input_path: Path,
        train_output_path: Path,
        validation_output_path: Path,
        validation_days: int = 28
    ) -> None:

        logger.info(
            "Loading feature dataset"
        )

        df = pl.read_parquet(
            input_path
        )

        logger.info(
            "Finding latest day"
        )

        latest_day = (
            df.select(
                pl.col(
                    "day_number"
                ).max()
            )
            .item()
        )

        validation_start_day = (
            latest_day
            - validation_days
            + 1
        )

        logger.info(
            f"Latest day: "
            f"{latest_day}"
        )

        logger.info(
            f"Validation starts: "
            f"{validation_start_day}"
        )

        logger.info(
            "Creating train dataset"
        )

        train_df = df.filter(
            pl.col("day_number")
            < validation_start_day
        )

        logger.info(
            "Creating validation dataset"
        )

        validation_df = df.filter(
            pl.col("day_number")
            >= validation_start_day
        )

        train_output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        validation_output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        logger.info(
            "Writing train dataset"
        )

        train_df.write_parquet(
            train_output_path
        )

        logger.info(
            "Writing validation dataset"
        )

        validation_df.write_parquet(
            validation_output_path
        )

        logger.info(
            "Dataset split completed"
        )

        logger.info(
            f"Train rows: "
            f"{train_df.height}"
        )

        logger.info(
            f"Validation rows: "
            f"{validation_df.height}"
        )