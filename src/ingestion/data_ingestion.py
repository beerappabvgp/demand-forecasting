from pathlib import Path

from src.common.logger import logger
from src.common.exceptions import DatasetNotFoundException

from src.ingestion.config import DataIngestionConfig

from src.ingestion.registration.dataset_registration import (
    DatasetRegistration
)

from src.ingestion.downloaders.kaggle_downloader import (
    KaggleDownloader
)

from src.ingestion.validators.dataset_validator import (
    DatasetValidator
)

from src.ingestion.validators.schema_validator import (
    SchemaValidator
)


class DataIngestion:

    def __init__(self):

        self.config = DataIngestionConfig()

    def verify_dataset_directory(
        self
    ) -> Path:

        dataset_path = (
            self.config.raw_data_dir
        )

        logger.info(
            f"Checking dataset directory: "
            f"{dataset_path}"
        )

        if not dataset_path.exists():

            raise DatasetNotFoundException(
                f"Dataset directory not found: "
                f"{dataset_path}"
            )

        logger.info(
            "Dataset directory verified"
        )

        return dataset_path

    def download_dataset(self):

        downloader = (
            KaggleDownloader()
        )

        return downloader.download_dataset(
            competition_name=
            self.config.competition_name,

            download_path=
            self.config.downloads_dir
        )

    def register_dataset(self):

        dataset_path = (
            self.verify_dataset_directory()
        )

        registration_service = (
            DatasetRegistration()
        )

        return (
            registration_service.register_dataset(
                dataset_path
            )
        )

    def validate_dataset(self):

        validator = (
            DatasetValidator()
        )

        return validator.validate_dataset(
            self.config.extracted_dir
        )

    def validate_schema(self):

        validator = (
            SchemaValidator()
        )

        return validator.validate_schema(
            self.config.extracted_dir
        )

    def run_validation_pipeline(self):

        logger.info(
            "Starting validation pipeline"
        )

        self.validate_dataset()

        self.validate_schema()

        logger.info(
            "Validation pipeline completed"
        )

        return True