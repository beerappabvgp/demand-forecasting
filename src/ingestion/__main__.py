from src.ingestion.data_ingestion import DataIngestion


def main():

    ingestion = DataIngestion()

    download_path = (
        ingestion.download_dataset()
    )

    print(download_path)

    print(metadata)


if __name__ == "__main__":
    main()