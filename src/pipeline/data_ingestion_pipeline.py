from src.config.configuration import ConfigurationManager
from src.components.data_ingestion import DataIngestion
from src.logging.logger import logging
from src.exception.exception import CustomException
import sys
#hehe
STAGE_NAME = "Data Ingestion Stage"

class DataIngestionTrainingPipeline:
    def __init__(self):
        pass
    def initiate_data_ingestion(self) -> None:
        config_manager = ConfigurationManager()
        data_ingestion_config = config_manager.get_data_ingestion_config()
        ingestion = DataIngestion(config=data_ingestion_config)
        csv_path = ingestion.initiate_data_ingestion()
        logging.info(f"CSV created at: {csv_path}")

if __name__ == "__main__":
    try:
        logging.info(f">>>>>> Stage {STAGE_NAME} started <<<<<<")
        obj = DataIngestionTrainingPipeline()
        obj.initiate_data_ingestion()
        logging.info(f">>>>>> Stage {STAGE_NAME} completed <<<<<<\n\nx================x")
    except Exception as e:
        logging.error(f"Error in stage {STAGE_NAME}")
        raise CustomException(e, sys)