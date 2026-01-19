# Docker-Terraform Project

This project demonstrates a **Dockerized data pipeline** that loads NYC taxi data into a PostgreSQL database, integrates with pgAdmin, and is structured for Terraform workflow.

---

## Project Structure

```
Docker-Terraform-project/
│
├─ data/
│   ├─ green_tripdata_2025-11.parquet
│   └─ taxi_zone_lookup.csv
│
├─ pipeline.py
├─ Dockerfile
├─ docker-compose.yaml
├─ requirements.txt
└─ README.md
```

---

## Docker Setup

### Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "pipeline.py"]
```

### requirements.txt

```text
pandas
sqlalchemy
psycopg2-binary
pyarrow
```

### docker-compose.yaml

```yaml
version: '3.9'

services:
  db:
    image: postgres:17-alpine
    container_name: postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ny_taxi
    ports:
      - "5433:5432"
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: pgadmin@pgadmin.com
      PGADMIN_DEFAULT_PASSWORD: pgadmin
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin

  pipeline:
    build: .
    container_name: pipeline
    depends_on:
      - db
    environment:
      POSTGRES_HOST: db
      POSTGRES_PORT: 5432
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ny_taxi
    volumes:
      - .:/app
      - ./data:/app/data

volumes:
  vol-pgdata:
  vol-pgadmin_data:
```

---

## Python Pipeline (`pipeline.py`)

```python
import os
import time
import pandas as pd
from sqlalchemy import create_engine

# Wait for Postgres to be ready
time.sleep(10)

# Load environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_DB = os.getenv("POSTGRES_DB", "ny_taxi")

# Create SQLAlchemy engine
engine = create_engine(
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Load taxi zones
zones_df = pd.read_csv("data/taxi_zone_lookup.csv")
zones_df.to_sql("zones", engine, if_exists="replace", index=False)
print("Taxi zone lookup loaded successfully!")

# Load green taxi trips parquet file
trips_df = pd.read_parquet("data/green_tripdata_2025-11.parquet")
trips_df.to_sql("trips", engine, if_exists="replace", index=False)
print("Green taxi trips loaded successfully!")

# List files in data folder
print("Files in /app/data:", os.listdir("/app/data"))
```

---

## Running the Project

1. Build and start all services:

```bash
docker-compose up --build
```

2. Check pipeline logs:

```bash
docker-compose logs -f pipeline
```

3. Access **pgAdmin** at `http://localhost:8080` and connect to the database using:

   * **Hostname**: `db`
   * **Port**: `5432`
   * **Username**: `postgres`
   * **Password**: `postgres`
   * **Database**: `ny_taxi`

---

## Example SQL Queries

### Trips ≤ 1 mile in November 2025

```sql
SELECT *
FROM trips
WHERE lpep_pickup_datetime >= '2025-11-01'
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance <= 1;
```

### Pickup day with longest trip (<100 miles)

```sql
SELECT DATE(lpep_pickup_datetime) AS pickup_date,
       MAX(trip_distance) AS longest_trip
FROM trips
WHERE trip_distance < 100
GROUP BY pickup_date
ORDER BY longest_trip DESC
LIMIT 1;
```

### Pickup zone with largest total_amount on Nov 18, 2025

```sql
SELECT z.Zone, SUM(t.total_amount) AS total_amount
FROM trips t
JOIN zones z ON t.PULocationID = z.LocationID
WHERE DATE(t.lpep_pickup_datetime) = '2025-11-18'
GROUP BY z.Zone
ORDER BY total_amount DESC
LIMIT 1;
```

### Dropoff zone with largest tip for pickups in East Harlem North

```sql
SELECT z.Zone, MAX(t.tip_amount) AS max_tip
FROM trips t
JOIN zones z ON t.DOLocationID = z.LocationID
WHERE t.PULocationID = (
    SELECT LocationID FROM zones WHERE Zone = 'East Harlem North'
)
AND t.lpep_pickup_datetime >= '2025-11-01'
AND t.lpep_pickup_datetime < '2025-12-01'
GROUP BY z.Zone
ORDER BY max_tip DESC
LIMIT 1;
```

---

## Terraform Workflow

Typical workflow:

```text
terraform init
terraform apply -auto-approve
terraform destroy
```

---

## Saving Progress

If stopping work, use:

```bash
docker-compose down
```

Later, restart with:

```bash
docker-compose up
```

---

## GitHub

Repository URL: [https://github.com/fay-cloud/Docker-terraform-project](https://github.com/fay-cloud/Docker-terraform-project)
