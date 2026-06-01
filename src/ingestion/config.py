from dataclasses import dataclass
from pathlib import Path


@dataclass
class DataIngestionConfig:

    raw_data_dir: Path = Path("data/raw/m5")

    downloads_dir: Path = Path(
        "data/raw/m5/downloads"
    )

    sales_dir: Path = Path(
        "data/raw/m5/sales"
    )

    calendar_dir: Path = Path(
        "data/raw/m5/calendar"
    )

    prices_dir: Path = Path(
        "data/raw/m5/prices"
    )

    metadata_dir: Path = Path(
        "data/raw/m5/metadata"
    )