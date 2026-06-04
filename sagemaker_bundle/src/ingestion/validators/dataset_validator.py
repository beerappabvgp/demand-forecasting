from pathlib import Path

from src.common.logger import logger


class DatasetValidator:

    REQUIRED_FILES = [
        "calendar.csv",
        "sales_train_validation.csv",
        "sell_prices.csv"
    ]

    def validate_dataset(
        self,
        dataset_path: Path
    ) -> bool:

        logger.info(
            "Starting dataset validation"
        )

        for file_name in self.REQUIRED_FILES:

            file_path = (
                dataset_path / file_name
            )

            if not file_path.exists():

                raise FileNotFoundError(
                    f"Missing file: "
                    f"{file_name}"
                )

            if file_path.stat().st_size == 0:

                raise ValueError(
                    f"Empty file: "
                    f"{file_name}"
                )

            logger.info(
                f"Validated: {file_name}"
            )

        logger.info(
            "Dataset validation completed"
        )

        return True