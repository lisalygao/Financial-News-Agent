# STAGE 1: Build the React Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --silent
COPY frontend/ ./
RUN npm run build

# STAGE 2: Build the Python Backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything (including the backend folder)
COPY . .

# Copy the built frontend into backend/static
# This matches the 'DIST = os.path.join(os.path.dirname(__file__), "static")' in your main.py
COPY --from=frontend-builder /app/frontend/dist ./backend/static

# CRITICAL: Fix for module import errors
ENV PYTHONPATH=/app
ENV PORT=8080

# Verify the app imports cleanly
RUN python -c "from backend.main import app; print('Import check passed')"

CMD ["sh", "-c", "exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1"]