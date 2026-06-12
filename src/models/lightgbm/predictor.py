import pandas as pd


class LightGBMPredictor:

    def predict(
        self,
        model,
        dataset: pd.DataFrame
    ):

        predictions = (
            model.predict(
                dataset
            )
        )

        return predictions