from pathlib import Path
import subprocess

from src.common.logger import logger


class KaggleDownloader:

    def download_dataset(
        self,
        competition_name: str,
        download_path: Path
    ) -> Path:

        logger.info(
            f"Downloading dataset from competition: "
            f"{competition_name}"
        )

        download_path.mkdir(
            parents=True,
            exist_ok=True
        )

        command = [
            "kaggle",
            "competitions",
            "download",
            "-c",
            competition_name,
            "-p",
            str(download_path)
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:

            raise RuntimeError(
                f"Dataset download failed:\n"
                f"{result.stderr}"
            )

        logger.info(
            "Dataset downloaded successfully"
        )

        return download_path