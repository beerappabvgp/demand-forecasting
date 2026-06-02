import polars as pl


def main():

    df = pl.read_parquet(
        "data/features/intermediate/sales_long.parquet"
    )

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns)

    print("\nSample:")
    print(df.head())


if __name__ == "__main__":
    main()