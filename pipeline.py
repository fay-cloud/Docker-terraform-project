import os
import time
import pandas as pd
from sqlalchemy import create_engine


time.sleep(10)

# environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_DB = os.getenv("POSTGRES_DB", "ny_taxi")

# SQLAlchemy engine
engine = create_engine(
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

data_dir = "/app/data"


print("Files in /app/data:", os.listdir(data_dir))

# Load taxi zones safely
taxi_zones_file = os.path.join(data_dir, "taxi_zone_lookup.csv")
if os.path.exists(taxi_zones_file):
    zones_df = pd.read_csv(taxi_zones_file)
    zones_df.to_sql("zones", engine, if_exists="replace", index=False)
    print("Taxi zone lookup loaded successfully!")
else:
    print(f"Error: {taxi_zones_file} not found!")

# Load green taxi trips safely
green_trips_file = os.path.join(data_dir, "green_tripdata_2025-11.parquet")
if os.path.exists(green_trips_file):
    trips_df = pd.read_parquet(green_trips_file)
    trips_df.to_sql("trips", engine, if_exists="replace", index=False)
    print("Green taxi trips loaded successfully!")
else:
    print(f"Error: {green_trips_file} not found!")
