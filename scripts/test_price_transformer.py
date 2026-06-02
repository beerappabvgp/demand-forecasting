from pathlib import Path

from src.features.transforms.price_transformer import (
    PriceTransformer
)


def main():

    transformer = (
        PriceTransformer()
    )

    transformer.transform(

        input_path=Path(
            "data/raw/m5/extracted/sell_prices.csv"
        ),

        output_path=Path(
            "data/features/intermediate/price_features.parquet"
        )
    )


if __name__ == "__main__":
    main()