from dataclasses import dataclass


@dataclass
class DatasetMetadata:

    dataset_name: str

    source: str

    version: str

    status: str