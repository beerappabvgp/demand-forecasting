from pathlib import Path
import zipfile

from src.common.logger import logger


class ZipExtractor:

    def extract_zip_file(
        self,
        zip_file_path: Path,
        destination_path: Path
    ) -> None:

        logger.info(
            f"Extracting: {zip_file_path}"
        )

        with zipfile.ZipFile(
            zip_file_path,
            "r"
        ) as zip_ref:

            zip_ref.extractall(
                destination_path
            )

        logger.info(
            f"Extraction completed: "
            f"{zip_file_path}"
        )
