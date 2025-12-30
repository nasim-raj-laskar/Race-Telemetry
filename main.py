from src.logging.logger import logging
from src.exception.exception import CustomException
import sys
from src.pipeline.data_ingestion_pipeline import DataIngestionTrainingPipeline
from src.pipeline.data_validation_pipeline import DataValidationTrainingPipeline
from src.pipeline.data_transformation_pipeline import DataTransformationTrainingPipeline
from src.pipeline.model_trainer_pipeline import ModelTrainerPipeline
from src.pipeline.model_evaluation_pipeline import ModelEvaluationPipeline

STAGE_NAME = "Data Ingestion Stage"
try:
    logging.info(f">>>>>> Stage {STAGE_NAME} started <<<<<<")
    # obj = DataIngestionTrainingPipeline()
    # obj.initiate_data_ingestion()
    logging.info(f">>>>>> Stage {STAGE_NAME} completed <<<<<<\n\nx================x")
except Exception as e:
    logging.error(f"Error in stage {STAGE_NAME}")
    raise CustomException(e, sys)

STAGE_NAME = "Data Validation Stage"
try:
    logging.info(f">>>>>> {STAGE_NAME} started <<<<<<")
    obj = DataValidationTrainingPipeline()
    obj.initiate_data_validation()
    logging.info(f">>>>>> {STAGE_NAME} completed <<<<<<\n\nx==========x")
except Exception as e:
    logging.exception(e)
    raise CustomException(e, sys)

STAGE_NAME = "Data Transformation Stage"
try:
    logging.info(f">>>>>> {STAGE_NAME} started <<<<<<")
    obj = DataTransformationTrainingPipeline()
    obj.initiate_data_transformation()
    logging.info(f">>>>>> {STAGE_NAME} completed <<<<<<\n\nx==========x")
except Exception as e:
    logging.exception(e)
    raise CustomException(e, sys)

STAGE_NAME = "Model Trainer Stage"
try:
    logging.info(f">>>>>> {STAGE_NAME} started <<<<<<")
    obj = ModelTrainerPipeline()
    obj.initiate_model_trainer()
    logging.info(f">>>>>> {STAGE_NAME} completed <<<<<<\n\nx==========x")
except Exception as e:
    logging.exception(e)
    raise CustomException(e, sys)

STAGE_NAME = "Model Evaluation Stage"
try:
    logging.info(f">>>>>> {STAGE_NAME} started <<<<<<")
    obj = ModelEvaluationPipeline()
    obj.initiate_model_evaluation()
    logging.info(f">>>>>> {STAGE_NAME} completed <<<<<<\n\nx==========x")
except Exception as e:
    logging.exception(e)
    raise CustomException(e, sys)