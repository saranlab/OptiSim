FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for scipy & highs solver
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ab_testing_platform/ ./ab_testing_platform/
COPY backend/ ./backend/
COPY sample_experiment_data.csv .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
