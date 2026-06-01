from dataclasses import dataclass
from pathlib import Path


@dataclass
class DataIngestionConfig:

    competition_name: str = (
        "m5-forecasting-accuracy"
    )

    raw_data_dir: Path = Path(
        "data/raw/m5"
    )

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
    
    extracted_dir: Path = Path(
        "data/raw/m5/extracted"
    )