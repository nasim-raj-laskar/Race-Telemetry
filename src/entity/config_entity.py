from dataclasses import dataclass
from pathlib import Path

@dataclass
class DataIngestionConfig:
    root_dir: Path
    MONGO_DB_URL: str
    DATABASE_NAME: str
    COLLECTION_NAME: str
    local_data_file: Path

@dataclass
class DataValidationConfig:
    root_dir: Path
    local_data_file: Path
    STATUS_FILE: Path