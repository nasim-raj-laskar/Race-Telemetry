import pandas as pd
from sklearn.model_selection import train_test_split
from src.features.features import engineer_telemetry_features
from src.exception.exception import CustomException
from src.logging.logger import logging
import sys

class DataTransformation:
    def __init__(self, config, features_config):
        self.config = config
        self.features = features_config

    def initiate_data_transformation(self):
        try:
            logging.info("Starting data transformation")
            df = pd.read_csv(self.config.raw_data_path)
            logging.info(f"Raw data loaded with shape: {df.shape}")
            # Feature engineering
            df_before = df.shape[0]
            df = engineer_telemetry_features(df)
            logging.info(
                f"Feature engineering completed | "
                f"Rows before: {df_before}, after: {df.shape[0]}"
            )

            # Drop columns
            drop_cols = self.features["DROP_COLUMNS"]
            existing_drop_cols = [c for c in drop_cols if c in df.columns]
            df.drop(columns=existing_drop_cols, inplace=True)

            logging.info(f"Dropped columns: {existing_drop_cols}")
            logging.info(f"Shape after column drop: {df.shape}")

            # Select final columns
            final_columns = (
                self.features["NUMERIC_FEATURES"]
                + self.features["CATEGORICAL_FEATURES"]
                + self.features["LABEL_COLUMNS"]
            )

            missing_cols = [c for c in final_columns if c not in df.columns]
            if missing_cols:
                logging.warning(f"Missing expected columns: {missing_cols}")

            df = df[list(dict.fromkeys(final_columns))]
            logging.info(f"Final feature set size: {df.shape[1]} columns")

            # Save processed data
            df.to_csv(self.config.processed_file_path, index=False)
            logging.info(
                f"Processed dataset saved at: {self.config.processed_file_path}"
            )

            # Split data
            train_val, test = train_test_split(
                df, test_size=0.15, random_state=42
            )
            train, val = train_test_split(
                train_val, test_size=0.1765, random_state=42
            )

            logging.info(
                f"Data split completed | "
                f"Train: {train.shape}, "
                f"Val: {val.shape}, "
                f"Test: {test.shape}"
            )

            # Save splits
            train.to_csv(self.config.train_path, index=False)
            val.to_csv(self.config.val_path, index=False)
            test.to_csv(self.config.test_path, index=False)

            logging.info("Data transformation completed successfully")

        except Exception as e:
            logging.error("Data transformation failed", exc_info=True)
            raise CustomException(e, sys)