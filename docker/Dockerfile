FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (e.g. for ta-lib if needed, or asyncpg)
RUN apt-get update && apt-get install -y gcc g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set Python Path
ENV PYTHONPATH=/app

# Command to run API (Override this in docker-compose for the scheduler)
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
