import pickle


class ModelStore:

    def save(
        self,
        model,
        path: str
    ) -> None:

        with open(
            path,
            "wb"
        ) as file:

            pickle.dump(
                model,
                file
            )

    def load(
        self,
        path: str
    ):

        with open(
            path,
            "rb"
        ) as file:

            model = (
                pickle.load(
                    file
                )
            )

        return model