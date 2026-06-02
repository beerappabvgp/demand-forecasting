from pathlib import Path

from src.features.engineering.lag_feature_engineer import (
    LagFeatureEngineer
)


def main():

    engineer = (
        LagFeatureEngineer()
    )

    engineer.build(

        input_path=Path(
            "data/features/final/training_dataset.parquet"
        ),

        output_path=Path(
            "data/features/final/feature_dataset.parquet"
        )
    )


if __name__ == "__main__":
    main()