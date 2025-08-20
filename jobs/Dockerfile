FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY jobs/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary project code (avoid copying local virtualenvs)
COPY jobs/config.yaml ./config.yaml
COPY jobs/scheduler.py ./scheduler.py
COPY jobs/etl ./etl
COPY jobs/utils ./utils
COPY jobs/task ./task

# Default command: run scheduler
CMD ["python", "scheduler.py"]


