from pathlib import Path

from src.features.builders.training_dataset_builder import (
    TrainingDatasetBuilder
)


def main():

    builder = (
        TrainingDatasetBuilder()
    )

    builder.build(

        sales_path=Path(
            "data/features/intermediate/sales_long.parquet"
        ),

        calendar_path=Path(
            "data/features/intermediate/calendar_features.parquet"
        ),

        price_path=Path(
            "data/features/intermediate/price_features.parquet"
        ),

        output_path=Path(
            "data/features/final/training_dataset.parquet"
        )
    )


if __name__ == "__main__":
    main()