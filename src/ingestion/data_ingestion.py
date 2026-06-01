from pathlib import Path
from src.ingestion.registration.dataset_registration import DatasetRegistration
from src.common.logger import logger
from src.common.exceptions import DatasetNotFoundException
from src.ingestion.config import DataIngestionConfig
from src.ingestion.downloaders.kaggle_downloader import (
    KaggleDownloader
)

class DataIngestion:

    def __init__(self):
        self.config = DataIngestionConfig()

    def verify_dataset_directory(self) -> Path:

        dataset_path = self.config.raw_data_dir

        logger.info(
            f"Checking dataset directory: {dataset_path}"
        )

        if not dataset_path.exists():
            raise DatasetNotFoundException(
                f"Dataset directory not found: {dataset_path}"
            )

        logger.info("Dataset directory verified")

        return dataset_path

    def register_dataset(self):

        dataset_path = (
            self.verify_dataset_directory()
        )

        registration_service = (
            DatasetRegistration()
        )

        metadata = (
            registration_service.register_dataset(
                dataset_path
            )
        )

        return metadata
    
    def download_dataset(self):

        downloader = KaggleDownloader()

        dataset_path = (
            downloader.download_dataset(
                self.config.competition_name
            )
        )

        return dataset_path