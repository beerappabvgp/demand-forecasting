from pathlib import Path

from src.validation.profiling.data_profiler import (
    DataProfiler
)


def main():

    profiler = (
        DataProfiler()
    )

    files = [

        Path(
            "data/raw/m5/extracted/calendar.csv"
        ),

        Path(
            "data/raw/m5/extracted/sell_prices.csv"
        ),

        Path(
            "data/raw/m5/extracted/sales_train_validation.csv"
        )
    ]

    for file_path in files:

        profile = (
            profiler.profile_csv(
                file_path
            )
        )

        print("\n")
        print("=" * 80)
        print(profile)
        print("=" * 80)


if __name__ == "__main__":
    main()