from pathlib import Path

import pandas as pd

from src.common.logger import logger


class SchemaValidator:

    REQUIRED_SCHEMAS = {

        "calendar.csv": [
            "date",
            "wm_yr_wk",
            "weekday",
            "month",
            "year"
        ],

        "sell_prices.csv": [
            "store_id",
            "item_id",
            "wm_yr_wk",
            "sell_price"
        ],

        "sales_train_validation.csv": [
            "id",
            "item_id",
            "dept_id",
            "cat_id",
            "store_id",
            "state_id"
        ]
    }

    def validate_schema(
        self,
        dataset_path: Path
    ) -> bool:

        logger.info(
            "Starting schema validation"
        )

        for file_name, required_columns in (
            self.REQUIRED_SCHEMAS.items()
        ):

            file_path = (
                dataset_path / file_name
            )

            df = pd.read_csv(
                file_path,
                nrows=5
            )

            actual_columns = (
                set(df.columns)
            )

            for column in required_columns:

                if column not in actual_columns:

                    raise ValueError(
                        f"{file_name} missing column: "
                        f"{column}"
                    )

            logger.info(
                f"Schema validated: "
                f"{file_name}"
            )

        logger.info(
            "Schema validation completed"
        )

        return True