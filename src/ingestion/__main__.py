from src.ingestion.data_ingestion import DataIngestion


def main():

    ingestion = DataIngestion()

    dataset_path = (
        ingestion.verify_dataset_directory()
    )

    print(
        f"Dataset verified: {dataset_path}"
    )


if __name__ == "__main__":
    main()
