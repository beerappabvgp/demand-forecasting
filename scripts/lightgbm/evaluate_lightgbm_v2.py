import polars as pl

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error
)

from src.training.dataset_loader import (
    DatasetLoader
)

from src.models.lightgbm.model_store import (
    ModelStore
)

from src.models.lightgbm.trainer import (
    LightGBMTrainer
)


def main():

    print(
        "Loading validation dataset"
    )

    loader = DatasetLoader()

    df = (
        loader.load_validation_data(
            "data/training/validation_dataset.parquet"
        )
    )

    print(
        f"Rows: {df.height}"
    )

    pandas_df = (
        df.to_pandas()
    )

    trainer = (
        LightGBMTrainer()
    )

    X = pandas_df[
        trainer.FEATURE_COLUMNS
    ]

    y = pandas_df[
        "target_sales"
    ]

    print(
        "Loading model"
    )

    model = (
        ModelStore()
        .load(
            "models/lightgbm_model.pkl"
        )
    )

    print(
        "Generating predictions"
    )

    predictions = (
        model.predict(X)
    )

    print(
        "Calculating MAE"
    )

    mae = (
        mean_absolute_error(
            y,
            predictions
        )
    )

    print(
        "Calculating RMSE"
    )

    rmse = (
        mean_squared_error(
            y,
            predictions
        ) ** 0.5
    )

    print()

    print(
        f"MAE  : {mae:.4f}"
    )

    print(
        f"RMSE : {rmse:.4f}"
    )


if __name__ == "__main__":
    main()