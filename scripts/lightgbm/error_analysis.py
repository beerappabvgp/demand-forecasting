import pandas as pd

from src.training.dataset_loader import (
    DatasetLoader
)

from src.models.lightgbm.model_store import (
    ModelStore
)

from src.models.lightgbm.trainer import (
    LightGBMTrainer
)


TOP_N = 10


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

    results = pd.DataFrame(
        {
            "item_id":
                pandas_df["item_id"],

            "store_id":
                pandas_df["store_id"],

            "date":
                pandas_df["date"],

            "lag_1":
                pandas_df["lag_1"],

            "lag_7":
                pandas_df["lag_7"],

            "lag_28":
                pandas_df["lag_28"],

            "rolling_mean_7":
                pandas_df["rolling_mean_7"],

            "rolling_mean_28":
                pandas_df["rolling_mean_28"],

            "actual":
                y,

            "predicted":
                predictions
        }
    )
    
    results["error"] = (
        results["actual"]
        - results["predicted"]
    ).abs()

    results = (
        results
        .sort_values(
            "error",
            ascending=False
        )
    )

    print()

    print(
        f"Top {TOP_N} Errors"
    )

    print("-" * 100)

    print(
        results.head(TOP_N)
    )


if __name__ == "__main__":
    main()