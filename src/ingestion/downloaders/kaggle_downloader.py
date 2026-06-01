from pathlib import Path

import kagglehub

from src.common.logger import logger


class KaggleDownloader:

    def download_dataset(
        self,
        competition_name: str
    ) -> Path:

        logger.info(
            f"Downloading dataset: "
            f"{competition_name}"
        )

        dataset_path = (
            kagglehub.competition_download(
                competition_name
            )
        )

        logger.info(
            f"Dataset downloaded to: "
            f"{dataset_path}"
        )

        return Path(dataset_path)