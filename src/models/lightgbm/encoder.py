import polars as pl


class LabelEncoder:

    def __init__(self):

        self.mappings = {}

    def fit_transform(
        self,
        dataset: pl.DataFrame,
        columns: list[str]
    ) -> pl.DataFrame:

        result = dataset

        for column in columns:

            categories = (
                result
                .select(column)
                .unique()
                .sort(column)
                .to_series()
                .to_list()
            )

            mapping = {
                value: index
                for index, value
                in enumerate(categories)
            }

            self.mappings[column] = mapping

            result = (
                result
                .with_columns(
                    pl.col(column)
                    .replace(mapping)
                    .cast(pl.Int32)
                )
            )

        return result