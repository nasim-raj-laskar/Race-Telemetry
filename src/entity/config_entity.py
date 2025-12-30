from dataclasses import dataclass
from pathlib import Path
from typing import Dict

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

@dataclass
class DataTransformationConfig:
    raw_data_path: Path
    processed_dir: Path
    processed_file_path: Path
    train_path: Path
    val_path: Path
    test_path: Path

@dataclass
class ModelTrainerConfig:
    model_root_dir:Path
    train_path:Path
    val_path:Path
    regression_dir:Path
    classification_dir:Path
    clustering_dir:Path

@dataclass
class ModelEvaluationConfig:
    root_dir: Path
    val_path: Path
    model_paths: Dict[str, Path]
    scaler_paths: Dict[str, Path]
    metrics_path: Path