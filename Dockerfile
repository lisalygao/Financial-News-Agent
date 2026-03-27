# STAGE 1: Build the React Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
# Copy only the files needed to install dependencies
COPY frontend/package*.json ./
RUN npm ci --silent
# Copy the rest of the frontend and build it
COPY frontend/ ./
RUN npm run build

# STAGE 2: Build the Python Backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for PostgreSQL (psycopg2)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY . .

# Copy the built frontend from Stage 1 into the backend's static folder
# (Adjust 'backend/static' to match where your FastAPI/Flask looks for files)
COPY --from=frontend-builder /app/frontend/dist ./backend/static

ENV PORT=8080
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]