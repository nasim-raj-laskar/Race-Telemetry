from src.logging.logger import logging
from src.exception.exception import CustomException
import sys
import pandas as pd
from src.entity.config_entity import DataValidationConfig

class DataValidation:
    def __init__(self, config: DataValidationConfig, schema: dict):
        self.config = config
        self.schema = schema["COLUMNS"]

    def validate_all_columns(self) -> bool:
        try:
            df = pd.read_csv(self.config.local_data_file)
            df.columns = df.columns.str.strip()
            csv_cols = set(df.columns)
            schema_cols = set(self.schema.keys())
            missing_cols = schema_cols - csv_cols
            extra_cols = csv_cols - schema_cols
            validation_status = True

            with open(self.config.STATUS_FILE, "w") as f:
                if missing_cols:
                    validation_status = False
                    f.write(f"Missing columns: {list(missing_cols)}\n")
                if extra_cols:
                    f.write(f"Extra columns (allowed): {list(extra_cols)}\n")
                f.write(f"Validation status: {validation_status}\n")

            return validation_status

        except Exception as e:
            raise CustomException(e, sys)