import sys
import pandas as pd
import pymongo
import certifi
from pathlib import Path
from src.logging.logger import logging
from src.exception.exception import CustomException
from src.entity.config_entity import DataIngestionConfig


class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        try:
            self.config = config

            self.mongo_client = pymongo.MongoClient(
                self.config.MONGO_DB_URL,
                tlsCAFile=certifi.where()
            )

            logging.info("MongoDB client initialized successfully.")

        except Exception as e:
            logging.error("Error initializing DataIngestion.")
            raise CustomException(e, sys)

    def export_collection_as_dataframe(self) -> pd.DataFrame:
        """
        Extract MongoDB collection and return DataFrame
        """
        try:
            logging.info(
                f"Extracting data from MongoDB: "
                f"{self.config.DATABASE_NAME}.{self.config.COLLECTION_NAME}"
            )

            collection = self.mongo_client[
                self.config.DATABASE_NAME
            ][self.config.COLLECTION_NAME]

            data = list(collection.find())

            if not data:
                raise Exception("MongoDB collection is empty.")

            df = pd.DataFrame(data)

            logging.info(
                f"Data extracted successfully | Shape: {df.shape}"
            )

            return df

        except Exception as e:
            logging.error("Error extracting data from MongoDB.")
            raise CustomException(e, sys)

    def export_data_to_local_csv(self, df: pd.DataFrame) -> Path:
        """
        Save extracted data as local CSV
        """
        try:
            output_path = Path(self.config.local_data_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            df.to_csv(output_path, index=False)

            logging.info(f"Data saved to local CSV: {output_path}")

            return output_path

        except Exception as e:
            logging.error("Error saving data to local CSV.")
            raise CustomException(e, sys)

    def initiate_data_ingestion(self) -> Path:
        """
        MongoDB → DataFrame → Local CSV
        """
        try:
            df = self.export_collection_as_dataframe()
            csv_path = self.export_data_to_local_csv(df)

            logging.info("Data ingestion completed successfully.")

            return csv_path

        except Exception as e:
            logging.error("Data ingestion pipeline failed.")
            raise CustomException(e, sys)
