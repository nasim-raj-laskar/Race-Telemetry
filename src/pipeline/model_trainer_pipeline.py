from src.config.configuration import ConfigurationManager
from src.logging.logger import logging
from src.exception.exception import CustomException
from src.components.model_trainer import ModelTrainer
import sys

STAGE_NAME = "Model Trainer Stage"

class ModelTrainerPipeline:
    def __init__(self):
        pass

    def initiate_model_trainer(self):
        try:
            config=ConfigurationManager()
            model_trainer_config = config.get_model_trainer_config()
            model_trainer = ModelTrainer(model_trainer_config,config.models,config.features,config.params)
            model_trainer.initiate_model_training()
            logging.info("Model training completed successfully")
        except Exception as e:
            logging.error("Model training failed", exc_info=True)
            raise CustomException(e)
        
if __name__ == "__main__":
    try:
        logging.info(f">>>>>> {STAGE_NAME} started <<<<<<")
        obj = ModelTrainerPipeline()
        obj.initiate_model_trainer()
        logging.info(f">>>>>> {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logging.exception(e)
        raise CustomException(e, sys)