import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

# Load CSV
df = pd.read_csv("artifacts/data_transformation/test.csv")

# Push to Postgres
df.to_sql(
    "my_table",        
    engine,
    if_exists="append",  
    index=False,
    method="multi"
)

print("CSV uploaded successfully")
