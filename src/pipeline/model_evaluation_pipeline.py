from src.config.configuration import ConfigurationManager
from src.logging.logger import logging
from src.exception.exception import CustomException
from src.components.model_evaluation import ModelEvaluation
import sys
from src.utils.mlfow_setup import setup_mlflow

STAGE_NAME = "Model Evaluation Stage"

class ModelEvaluationPipeline:
    def __init__(self):
        pass
    def initiate_model_evaluation(self):
        try:
            setup_mlflow()
            config_manager = ConfigurationManager()
            model_eval_config = config_manager.get_model_evaluation_config()
            evaluator = ModelEvaluation(model_eval_config, config_manager.features)
            evaluator.evaluate()
            logging.info("Model evaluation process finished successfully")
        except Exception as e:
            logging.error("Model evaluation process failed")
            raise CustomException(e, sys)
        

if __name__ == "__main__":
    try:
        logging.info(f">>>>>> {STAGE_NAME} started <<<<<<")
        obj = ModelEvaluationPipeline()
        obj.initiate_model_evaluation()
        logging.info(f">>>>>> {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logging.exception(e)
        raise CustomException(e, sys)