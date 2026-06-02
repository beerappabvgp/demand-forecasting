from pathlib import Path

from src.features.targets.target_generator import (
    TargetGenerator
)


def main():

    generator = (
        TargetGenerator()
    )

    generator.build(

        input_path=Path(
            "data/features/final/feature_dataset.parquet"
        ),

        output_path=Path(
            "data/features/final/model_dataset.parquet"
        )
    )


if __name__ == "__main__":
    main()