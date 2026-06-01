from pathlib import Path

import pandas as pd

from src.common.logger import logger


class DataProfiler:

    def profile_csv(
        self,
        file_path: Path
    ) -> dict:

        logger.info(
            f"Profiling: {file_path.name}"
        )

        df = pd.read_csv(
            file_path
        )

        profile = {

            "file_name":
                file_path.name,

            "rows":
                len(df),

            "columns":
                len(df.columns),

            "memory_mb":
                round(
                    df.memory_usage(
                        deep=True
                    ).sum()
                    / 1024
                    / 1024,
                    2
                ),

            "null_counts":
                df.isnull().sum().to_dict()
        }

        return profile