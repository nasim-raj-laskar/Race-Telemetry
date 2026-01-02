import os, sys, json
import certifi
import pymongo
import pandas as pd
from dotenv import load_dotenv
from src.exception.exception import CustomException
from src.logging.logger import logging

load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

class RaceDataExtract:
    def __init__(self):
        try:
            self.mongo_client = pymongo.MongoClient(
                MONGO_DB_URL,
                tlsCAFile=certifi.where()
            )
        except Exception as e:
            logging.error("Error connecting to MongoDB")
            raise CustomException(e, sys)

    def csv_to_json_convertor(self, file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = data.to_dict(orient="records")
            return records
        except Exception as e:
            logging.error("Error converting CSV to JSON")
            raise CustomException(e, sys)

    def insert_data_mongodb(self, records, database, collection):
        try:
            db = self.mongo_client[database]
            col = db[collection]
            col.insert_many(records)
            return len(records)
        except Exception as e:
            logging.error("Error inserting data into MongoDB")
            raise CustomException(e, sys)


if __name__ == "__main__":
    FILE_PATH = "dataset/data.csv"
    DATABASE = "Nasimrl"
    COLLECTION = "Race_data"

    extractor = RaceDataExtract()
    records = extractor.csv_to_json_convertor(FILE_PATH)
    print(f"{len(records)} records extracted from CSV")

    inserted = extractor.insert_data_mongodb(records, DATABASE, COLLECTION)
    print(f"{inserted} records inserted into MongoDB")
