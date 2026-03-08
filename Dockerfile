FROM python:3.12-alpine

WORKDIR /app

# Install dependencies first (better layer caching)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY run.py .
COPY backend/ backend/

# Data directory for SQLite persistence
RUN mkdir -p backend/data

EXPOSE 1337

CMD ["gunicorn", \
     "--bind", "0.0.0.0:1337", \
     "--workers", "2", \
     "--chdir", "backend", \
     "app:create_app()"]
