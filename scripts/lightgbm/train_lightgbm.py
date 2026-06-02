import polars as pl

from src.models.lightgbm.trainer import (
    LightGBMTrainer
)

from src.models.lightgbm.model_store import (
    ModelStore
)

TRAIN_ROWS = 500_000


def main():

    print(
        "Loading dataset"
    )

    df = (
        pl.read_parquet(
            "data/training/lightgbm_train_dataset.parquet"
        )
        .filter(
            pl.col("lag_28")
            .is_not_null()
        )
        .head(TRAIN_ROWS)
    )

    print(
        f"Rows: {df.height}"
    )

    print(
        "Converting to pandas"
    )

    pandas_df = (
        df.to_pandas()
    )

    trainer = (
        LightGBMTrainer()
    )

    print(
        "Training model"
    )

    model = (
        trainer.train(
            pandas_df
        )
    )

    store = (
        ModelStore()
    )

    model_path = (
        "models/lightgbm_model.pkl"
    )

    print(
        "Saving model"
    )

    store.save(
        model,
        model_path
    )

    print()

    print(
        "Training completed"
    )

    print(
        f"Saved model: {model_path}"
    )


if __name__ == "__main__":
    main()