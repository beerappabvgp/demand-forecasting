from src.models.lightgbm.model_store import (
    ModelStore
)

from src.models.lightgbm.trainer import (
    LightGBMTrainer
)


def main():

    print(
        "Loading model"
    )

    model = (
        ModelStore()
        .load(
            "models/lightgbm_model.pkl"
        )
    )

    trainer = (
        LightGBMTrainer()
    )

    feature_importances = (
        model.feature_importances_
    )

    results = list(
        zip(
            trainer.FEATURE_COLUMNS,
            feature_importances
        )
    )

    results.sort(
        key=lambda x: x[1],
        reverse=True
    )

    print()

    print(
        "Feature Importances"
    )

    print(
        "-" * 40
    )

    for feature, importance in results:

        print(
            f"{feature:<20} "
            f"{importance}"
        )


if __name__ == "__main__":
    main()