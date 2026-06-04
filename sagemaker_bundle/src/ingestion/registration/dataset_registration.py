from pathlib import Path

from src.common.logger import logger


class DatasetRegistration:

    def register_dataset(
        self,
        dataset_path: Path
    ) -> dict:

        logger.info(
            f"Registering dataset: {dataset_path}"
        )

        files = list(
            dataset_path.rglob("*")
        )

        file_count = len(
            [
                file
                for file in files
                if file.is_file()
            ]
        )

        metadata = {
            "dataset_path": str(dataset_path),
            "file_count": file_count,
        }

        logger.info(
            f"Dataset registration complete: {metadata}"
        )

        return metadata
