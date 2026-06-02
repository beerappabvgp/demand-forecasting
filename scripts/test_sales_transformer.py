from pathlib import Path

from src.features.transforms.sales_transformer import (
    SalesTransformer
)


def main():

    transformer = (
        SalesTransformer()
    )

    transformer.transform(

        input_path=Path(
            "data/raw/m5/extracted/sales_train_validation.csv"
        ),

        output_path=Path(
            "data/features/intermediate/sales_long.parquet"
        )
    )


if __name__ == "__main__":
    main()