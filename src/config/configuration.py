import os
from src.constants import *
from src.utils.common import *
from src.entity.config_entity import DataIngestionConfig, DataValidationConfig , DataTransformationConfig , ModelTrainerConfig
from dotenv import load_dotenv
load_dotenv()

class ConfigurationManager:
    def __init__(
        self,
        config_filepath=CONFIG_FILE_PATH,
        params_filepath=PARAMS_FILE_PATH,
        schema_filepath=SCHEMA_FILE_PATH,
        features_filepath=FEATURES_FILE_PATH,
        models_filepath=MODELS_FILE_PATH):

        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)
        self.schema = read_yaml(schema_filepath)
        self.features = read_yaml(features_filepath)
        self.models = read_yaml(models_filepath)

        create_directories([self.config.artifacts_root])

#----------------------------------------------------------------
    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion

        create_directories([config.root_dir])

        data_ingestion_config = DataIngestionConfig(
            root_dir=config.root_dir,
            MONGO_DB_URL=os.getenv("MONGO_DB_URL"),
            DATABASE_NAME=config.DATABASE_NAME,
            COLLECTION_NAME=config.COLLECTION_NAME,
            local_data_file=config.local_data_file
        )

        return data_ingestion_config
    
#----------------------------------------------------------------

    def get_data_validation_config(self) -> DataValidationConfig:
        config = self.config.data_validation
        create_directories([config.root_dir])

        data_validation_config = DataValidationConfig(
            root_dir=config.root_dir,
            local_data_file=config.local_data_file,
            STATUS_FILE=config.STATUS_FILE
        )

        return data_validation_config
    
#----------------------------------------------------------------
    def get_data_transformation_config(self) -> DataTransformationConfig:
        config = self.config.data_transformation

        create_directories([config.processed_dir])

        data_transformation_config = DataTransformationConfig(
            raw_data_path=Path(config.raw_data_path),
            processed_dir=Path(config.processed_dir),
            processed_file_path=Path(config.processed_file_path),
            train_path=Path(config.train_path),
            val_path=Path(config.val_path),
            test_path=Path(config.test_path),
        )

        return data_transformation_config
    
#----------------------------------------------------------------
    def get_model_trainer_config(self) -> ModelTrainerConfig:
        config = self.config.model_trainer

        create_directories([config.regression_dir, config.classification_dir, config.clustering_dir])

        model_trainer_config = ModelTrainerConfig(
            model_root_dir=Path(config.model_root_dir),
            train_path=Path(config.train_path),
            val_path=Path(config.val_path),
            regression_dir=Path(config.regression_dir),
            classification_dir=Path(config.classification_dir),
            clustering_dir=Path(config.clustering_dir),
       
        )

        return model_trainer_config