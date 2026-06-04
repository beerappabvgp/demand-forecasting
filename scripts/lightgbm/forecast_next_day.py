from src.training.dataset_loader import (
    DatasetLoader
)

from src.models.lightgbm.model_store import (
    ModelStore
)

from src.models.lightgbm.predictor import (
    LightGBMPredictor
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

    print(
        "Loading model"
    )

    model = (
        ModelStore()
        .load(
            "models/lightgbm_model.pkl"
        )
    )

    predictor = (
        LightGBMPredictor()
    )

    print(
        "Generating forecasts"
    )

    predictions = (
        predictor.predict(
            model,
            X
        )
    )

    print()

    print(
        "First 20 forecasts"
    )

    print("-" * 80)

        
    for i in range(20):

        item_id = (
            pandas_df.iloc[i]["item_id"]
        )

        actual = (
            pandas_df.iloc[i]["target_sales"]
        )

        predicted = (
            predictions[i]
        )

        print(
            f"Item: {item_id:<20} "
            f"Actual: {actual:<5} "
            f"Predicted: {predicted:.2f}"
        )

if __name__ == "__main__":
    main()