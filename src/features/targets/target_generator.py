from pathlib import Path

import polars as pl

from src.common.logger import logger


class TargetGenerator:

    def build(
        self,
        input_path: Path,
        output_path: Path
    ) -> Path:

        logger.info(
            "Loading feature dataset"
        )

        df = pl.read_parquet(
            input_path
        )

        logger.info(
            "Creating target column"
        )

        df = df.with_columns(

            pl.col("sales")
            .shift(-1)
            .over(
                ["item_id", "store_id"]
            )
            .alias("target")
        )

        logger.info(
            "Removing rows without target"
        )

        df = df.filter(
            pl.col("target")
            .is_not_null()
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        logger.info(
            "Writing model dataset"
        )

        df.write_parquet(
            output_path
        )

        logger.info(
            f"Saved model dataset: "
            f"{output_path}"
        )

        return output_path