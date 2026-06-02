from pathlib import Path

import polars as pl

from src.common.logger import logger


class PriceTransformer:

    def transform(
        self,
        input_path: Path,
        output_path: Path
    ) -> Path:

        logger.info(
            "Loading price dataset"
        )

        df = pl.read_csv(
            input_path
        )

        df = df.select(
            [
                "store_id",
                "item_id",
                "wm_yr_wk",
                "sell_price"
            ]
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        df.write_parquet(
            output_path
        )

        logger.info(
            f"Saved price features: "
            f"{output_path}"
        )

        return output_path