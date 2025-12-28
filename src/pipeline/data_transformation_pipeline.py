from src.config.configuration import ConfigurationManager
from src.logging.logger import logging
from src.exception.exception import CustomException
from src.components.data_transformation import DataTransformation
import sys

STAGE_NAME = "Data Transformation Stage"

class DataTransformationTrainingPipeline:
    def __init__(self):
        pass

    def initiate_data_transformation(self):
        try:
            config_manager = ConfigurationManager()
            data_transformation_config = config_manager.get_data_transformation_config()
            features_config = config_manager.features
            transformer = DataTransformation(data_transformation_config, features_config)
            transformer.initiate_data_transformation()
            logging.info(f"Data transformation completed successfully")
        except Exception as e:
            logging.error("Data transformation execution failed")
            raise CustomException(e, sys)
        
if __name__ == "__main__":
    try:
        logging.info(f">>>>>> {STAGE_NAME} started <<<<<<")
        obj = DataTransformationTrainingPipeline()
        obj.initiate_data_transformation()
        logging.info(f">>>>>> {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logging.exception(e)
        raise CustomException(e, sys)