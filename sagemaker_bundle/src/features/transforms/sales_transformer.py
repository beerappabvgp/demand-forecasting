from pathlib import Path

import polars as pl

from src.common.logger import logger


class SalesTransformer:

    META_COLUMNS = [
        "id",
        "item_id",
        "dept_id",
        "cat_id",
        "store_id",
        "state_id"
    ]

    def transform(
        self,
        input_path: Path,
        output_path: Path
    ) -> Path:

        logger.info(
            "Loading sales dataset"
        )

        df = pl.read_csv(
            input_path
        )

        day_columns = [

            column

            for column in df.columns

            if column.startswith("d_")
        ]

        logger.info(
            f"Found {len(day_columns)} "
            f"daily columns"
        )

        logger.info(
            "Converting wide format "
            "to long format"
        )

        long_df = df.unpivot(
            index=self.META_COLUMNS,
            on=day_columns,
            variable_name="day",
            value_name="sales"
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        long_df.write_parquet(
            output_path
        )

        logger.info(
            f"Saved transformed dataset: "
            f"{output_path}"
        )

        return output_path