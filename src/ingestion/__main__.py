from src.ingestion.data_ingestion import DataIngestion


def main():

    ingestion = DataIngestion()

    metadata = (
        ingestion.register_dataset()
    )

    print(metadata)


if __name__ == "__main__":
    main()