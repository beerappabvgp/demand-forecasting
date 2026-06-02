from pathlib import Path

from src.features.transforms.calendar_transformer import (
    CalendarTransformer
)


def main():

    transformer = (
        CalendarTransformer()
    )

    transformer.transform(

        input_path=Path(
            "data/raw/m5/extracted/calendar.csv"
        ),

        output_path=Path(
            "data/features/intermediate/calendar_features.parquet"
        )
    )


if __name__ == "__main__":
    main()