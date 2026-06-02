from pathlib import Path

import polars as pl

from src.common.logger import logger


class CalendarTransformer:

    def transform(
        self,
        input_path: Path,
        output_path: Path
    ) -> Path:

        logger.info(
            "Loading calendar dataset"
        )

        df = pl.read_csv(
            input_path
        )

        df = df.rename(
            {
                "d": "day"
            }
        )

        df = df.select(
            [
                "day",

                "date",

                "wm_yr_wk",

                "weekday",

                "wday",

                "month",

                "year",

                "event_name_1",

                "event_type_1",

                "event_name_2",

                "event_type_2",

                "snap_CA",

                "snap_TX",

                "snap_WI"
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
            f"Saved calendar features: "
            f"{output_path}"
        )

        return output_path