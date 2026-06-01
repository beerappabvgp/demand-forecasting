from src.ingestion.data_ingestion import (
    DataIngestion
)


def main():

    ingestion = DataIngestion()

    result = (
        ingestion.run_validation_pipeline()
    )

    print(
        f"Pipeline Result: {result}"
    )


if __name__ == "__main__":
    main()