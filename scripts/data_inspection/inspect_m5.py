import pandas as pd


def inspect_csv(file_path: str):

    print("\n")
    print("=" * 80)
    print(file_path)
    print("=" * 80)

    df = pd.read_csv(
        file_path,
        nrows=5
    )

    print("\nColumns:\n")
    print(df.columns.tolist())

    print("\nSample Data:\n")
    print(df.head())


def main():

    inspect_csv(
        "data/raw/m5/extracted/calendar.csv"
    )

    inspect_csv(
        "data/raw/m5/extracted/sell_prices.csv"
    )

    inspect_csv(
        "data/raw/m5/extracted/sales_train_validation.csv"
    )


if __name__ == "__main__":
    main()