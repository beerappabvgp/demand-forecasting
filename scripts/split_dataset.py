from pathlib import Path

from src.training.dataset_splitter import (
    DatasetSplitter
)


def main():

    splitter = (
        DatasetSplitter()
    )

    splitter.split(

        input_path=Path(
            "data/features/final/feature_dataset.parquet"
        ),

        train_output_path=Path(
            "data/training/train_dataset.parquet"
        ),

        validation_output_path=Path(
            "data/training/validation_dataset.parquet"
        )
    )


if __name__ == "__main__":
    main()