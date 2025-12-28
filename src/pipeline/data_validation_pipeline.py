from src.config.configuration import ConfigurationManager
from src.logging.logger import logging
from src.exception.exception import CustomException
from src.components.data_validation import DataValidation
import sys

STAGE_NAME = "Data Validation Stage"

class DataValidationTrainingPipeline:
    def __init__(self):
        pass

    def initiate_data_validation(self):
        try:
            config_manager = ConfigurationManager()
            validation_config = config_manager.get_data_validation_config()
            data_validation = DataValidation(config=validation_config,schema=config_manager.schema)
            status = data_validation.validate_all_columns()
            logging.info(f"Data validation completed with status: {status}")
        except Exception as e:
            logging.error("Data validation execution failed")
            raise CustomException(e, sys)

if __name__ == "__main__":
    try:
        logging.info(f">>>>>> {STAGE_NAME} started <<<<<<")
        obj = DataValidationTrainingPipeline()
        obj.initiate_data_validation()
        logging.info(f">>>>>> {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logging.exception(e)
        raise CustomException(e, sys)